"""
邮件发送模块 - 通过 SMTP 发送 HTML 邮件
支持 QQ邮箱、Gmail 等主流邮箱服务
"""
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)

# 默认 SMTP 配置
DEFAULT_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "use_ssl": True,
}


def send_email(
    to_addr: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_ssl: bool = True,
) -> bool:
    """
    发送 HTML 邮件
    
    参数:
        to_addr: 收件人邮箱
        subject: 邮件主题
        html_content: HTML 正文
        text_content: 纯文本正文（可选，兜底用）
        smtp_server: SMTP 服务器地址
        smtp_port: SMTP 端口
        username: 邮箱用户名
        password: 邮箱密码/授权码
        use_ssl: 是否使用 SSL
    
    返回:
        bool: 是否发送成功
    
    环境变量配置（优先级高于参数）:
        MAIL_SMTP_SERVER: SMTP 服务器
        MAIL_SMTP_PORT: SMTP 端口
        MAIL_USERNAME: 邮箱地址
        MAIL_PASSWORD: 邮箱授权码
        MAIL_TO: 收件邮箱
    """
    # 从环境变量读取配置（优先级最高）
    smtp_server = smtp_server or os.getenv("MAIL_SMTP_SERVER") or DEFAULT_CONFIG["smtp_server"]
    smtp_port = smtp_port or int(os.getenv("MAIL_SMTP_PORT", str(DEFAULT_CONFIG["smtp_port"])))
    username = username or os.getenv("MAIL_USERNAME") or ""
    password = password or os.getenv("MAIL_PASSWORD") or ""
    to_addr = to_addr or os.getenv("MAIL_TO") or ""
    
    if not username or not password:
        logger.error("邮箱配置不完整: 缺少 username 或 password")
        return False
    
    if not to_addr:
        logger.error("收件人邮箱未配置")
        return False
    
    # 构建邮件
    msg = MIMEMultipart("alternative")
    msg["From"] = username
    msg["To"] = to_addr
    msg["Subject"] = subject
    
    # 添加纯文本版本（兜底）
    if text_content:
        msg.attach(MIMEText(text_content, "plain", "utf-8"))
    
    # 添加 HTML 版本
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    # 发送
    try:
        if use_ssl:
            logger.info(f"通过 SSL 连接 {smtp_server}:{smtp_port}")
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            logger.info(f"通过 TLS 连接 {smtp_server}:{smtp_port}")
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
        
        logger.info(f"✅ 邮件发送成功 → {to_addr}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ SMTP 认证失败，请检查邮箱地址和授权码")
        logger.error("   QQ邮箱请在设置 → 账户 → 生成授权码（不是登录密码）")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP 发送失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 邮件发送异常: {e}")
        return False


def send_model_release_email(
    data: dict,
    html_content: str,
    text_summary: str,
    to_addr: Optional[str] = None,
) -> bool:
    """
    发送模型发布日报邮件（封装函数）
    
    参数:
        data: fetcher 返回的数据
        html_content: 格式化后的 HTML
        text_summary: 纯文本摘要（用于标题）
        to_addr: 收件邮箱（可选，默认从环境变量读取）
    """
    to_addr = to_addr or os.getenv("MAIL_TO") or ""
    
    if not data.get("success"):
        subject = f"[AI雷达] ⚠️ 数据获取失败 - {data.get('fetched_at', '')[:10]}"
    else:
        model_count = len(data.get("model_releases", []))
        date_str = data.get("generated_at", "")[:10] or "今日"
        subject = f"🚀 AI 模型雷达日报 {date_str} · {model_count} 条模型发布更新"
    
    return send_email(
        to_addr=to_addr,
        subject=subject,
        html_content=html_content,
        text_content=text_summary,
    )
