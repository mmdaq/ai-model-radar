#!/usr/bin/env python3
"""
AI Model Radar 主入口
自动获取 AIbase 最新模型发布信息并发送邮件日报
"""
import json
import logging
import os
import sys
from datetime import datetime

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.fetcher import get_model_releases
from src.formatter import build_html_email, build_text_summary
from src.mailer import send_model_release_email


def setup_logging():
    """配置日志"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def save_output(data: dict, html: str):
    """将数据保存到本地 output 目录（用于调试）"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存 HTML
    html_path = os.path.join(output_dir, f"model_radar_{timestamp}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    # 保存 JSON
    json_path = os.path.join(output_dir, f"model_radar_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return html_path, json_path


def main():
    """主流程"""
    setup_logging()
    logger = logging.getLogger("main")
    
    logger.info("=" * 50)
    logger.info("🚀 AI 模型雷达日报 启动")
    logger.info("=" * 50)
    
    # Step 1: 获取数据
    logger.info("📡 Step 1/3: 获取 AIbase 数据...")
    data = get_model_releases()
    
    if not data.get("success"):
        logger.error(f"❌ 数据获取失败: {data.get('error')}")
        # 仍然尝试发送错误通知
        html = build_html_email(data)
        text = build_text_summary(data)
        logger.info("📧 发送错误通知邮件...")
        send_model_release_email(data, html, text)
        return 1
    
    model_count = len(data.get("model_releases", []))
    aibase_count = data.get("total_aibase", 0)
    logger.info(f"✅ 获取成功: {model_count} 条模型发布 / AIbase 共 {aibase_count} 条")
    
    # Step 2: 生成邮件内容
    logger.info("📝 Step 2/3: 生成邮件内容...")
    html = build_html_email(data)
    text = build_text_summary(data)
    
    # Step 3: 保存本地 & 发送邮件
    logger.info("📧 Step 3/3: 发送邮件...")
    
    # 保存到本地（用于调试/归档）
    html_path, json_path = save_output(data, html)
    logger.info(f"💾 HTML 已保存: {html_path}")
    logger.info(f"💾 JSON 已保存: {json_path}")
    
    # 发送邮件
    success = send_model_release_email(data, html, text)
    
    if success:
        logger.info("🎉 任务完成！邮件已发送")
        return 0
    else:
        logger.error("❌ 邮件发送失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
