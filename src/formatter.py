"""
邮件格式化模块 - 将模型发布数据渲染为精美的 HTML 邮件
"""
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def _format_time(time_str: Optional[str]) -> str:
    """格式化时间显示"""
    if not time_str:
        return "时间未知"
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        china_tz = timezone.utc  # 简化处理，用 UTC+8
        # 转为北京时间
        from datetime import timedelta
        dt_cn = dt + timedelta(hours=8)
        return dt_cn.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return time_str


def _build_model_card(item: dict, index: int) -> str:
    """构建单条模型发布卡片"""
    title = item.get("title_zh", "无标题") or item.get("title_en", "无标题") or "无标题"
    url = item.get("url", "")
    pub_time = _format_time(item.get("published_at"))
    
    # 标签映射
    label_map = {
        "model_release": "🤖 模型发布",
        "ai_tech": "⚙️ 技术突破",
        "ai_product_update": "🚀 产品更新",
        "ai_general": "📰 AI 资讯",
        "agent_workflow": "🔄 Agent 工作流",
        "research_paper": "📄 研究论文",
        "infra_compute": "💻 算力基建",
    }
    label = item.get("ai_label", "")
    label_display = label_map.get(label, label)
    
    url_html = f'<a href="{url}" target="_blank" style="color:#7c3aed;text-decoration:none;font-weight:500;">🔗 查看原文 →</a>' if url else ""
    
    return f"""
    <div style="background:#ffffff;border-radius:12px;padding:20px;margin-bottom:16px;border:1px solid #e5e7eb;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <span style="background:#f3e8ff;color:#7c3aed;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;">{label_display}</span>
            <span style="color:#9ca3af;font-size:12px;">{pub_time}</span>
        </div>
        <div style="font-size:16px;font-weight:600;color:#1f2937;margin-bottom:10px;line-height:1.5;">
            #{index} {title}
        </div>
        <div style="font-size:14px;">
            {url_html}
        </div>
    </div>
    """


def build_html_email(data: dict) -> str:
    """
    构建完整 HTML 邮件内容
    
    参数:
        data: fetcher.get_model_releases() 返回的数据
    """
    if not data.get("success"):
        return _build_error_email(data.get("error", "未知错误"))
    
    model_releases = data.get("model_releases", [])
    all_aibase = data.get("all_aibase", [])
    generated_at = _format_time(data.get("generated_at"))
    fetched_at = _format_time(data.get("fetched_at"))
    
    # 构建模型发布卡片
    model_cards = ""
    if model_releases:
        for i, item in enumerate(model_releases, 1):
            model_cards += _build_model_card(item, i)
    else:
        model_cards = """
        <div style="background:#fef3c7;border-radius:12px;padding:20px;text-align:center;color:#92400e;">
            <p style="font-size:16px;font-weight:600;">📭 暂无模型发布信息</p>
            <p style="font-size:14px;">AIbase 最近 24 小时暂无模型发布/更新内容</p>
        </div>
        """
    
    # 如果是全部 AIbase 条目（兜底情况），展示所有
    extra_section = ""
    if model_releases and len(all_aibase) > len(model_releases):
        other_items = [
            item for item in all_aibase
            if item.get("ai_label") not in {"model_release", "ai_tech"}
        ]
        if other_items:
            other_cards = ""
            for i, item in enumerate(other_items[:5], 1):  # 最多展示5条
                title = item.get("title_zh", "无标题") or "无标题"
                url = item.get("url", "")
                url_html = f'<a href="{url}" target="_blank" style="color:#6b7280;">查看原文</a>' if url else ""
                other_cards += f"""
                <div style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <div style="font-size:14px;color:#4b5563;">{title}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:4px;">{url_html}</div>
                </div>
                """
            
            extra_section = f"""
            <div style="margin-top:32px;">
                <h3 style="color:#374151;font-size:18px;margin-bottom:16px;">📋 AIbase 其他动态</h3>
                <div style="background:#ffffff;border-radius:12px;padding:16px 20px;border:1px solid #e5e7eb;">
                    {other_cards}
                </div>
            </div>
            """
    
    # 组装完整 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;">
        <tr>
            <td align="center" style="padding:40px 16px;">
                <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;">
                    <!-- 头部 -->
                    <tr>
                        <td style="background:linear-gradient(135deg,#7c3aed,#6366f1);border-radius:16px 16px 0 0;padding:32px 40px;text-align:center;">
                            <h1 style="color:#ffffff;font-size:28px;margin:0 0 8px 0;">🚀 AI 模型雷达日报</h1>
                            <p style="color:rgba(255,255,255,0.85);font-size:15px;margin:0;">AIbase 最新模型发布信息 · 每日推送</p>
                        </td>
                    </tr>
                    <!-- 概要 -->
                    <tr>
                        <td style="background:#ffffff;padding:24px 40px;border-bottom:1px solid #e5e7eb;">
                            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px;">
                                <div style="text-align:center;flex:1;min-width:100px;">
                                    <div style="font-size:28px;font-weight:700;color:#7c3aed;">{len(model_releases)}</div>
                                    <div style="font-size:13px;color:#6b7280;">今日模型发布</div>
                                </div>
                                <div style="text-align:center;flex:1;min-width:100px;">
                                    <div style="font-size:28px;font-weight:700;color:#6366f1;">{data.get('total_aibase', 0)}</div>
                                    <div style="font-size:13px;color:#6b7280;">AIbase 资讯</div>
                                </div>
                                <div style="text-align:center;flex:1;min-width:100px;">
                                    <div style="font-size:28px;font-weight:700;color:#8b5cf6;">{data.get('total_items', 0)}</div>
                                    <div style="font-size:13px;color:#6b7280;">全网信号</div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <!-- 时间信息 -->
                    <tr>
                        <td style="background:#fafafa;padding:12px 40px;border-bottom:1px solid #e5e7eb;">
                            <div style="display:flex;justify-content:space-between;font-size:12px;color:#9ca3af;">
                                <span>📡 数据来源: AI News Radar → AIbase</span>
                                <span>🕐 数据生成: {generated_at}</span>
                            </div>
                        </td>
                    </tr>
                    <!-- 模型发布内容 -->
                    <tr>
                        <td style="background:#f9fafb;padding:24px 40px;">
                            <h2 style="color:#1f2937;font-size:20px;margin:0 0 20px 0;">
                                🤖 模型发布 & 技术更新
                                <span style="font-size:14px;color:#9ca3af;font-weight:400;">（共 {len(model_releases)} 条）</span>
                            </h2>
                            {model_cards}
                            {extra_section}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background:#1f2937;border-radius:0 0 16px 16px;padding:20px 40px;text-align:center;">
                            <p style="color:#9ca3af;font-size:12px;margin:0;">
                                AI Model Radar · 自动生成于 {fetched_at}<br>
                                数据来源: <a href="https://learnprompt.github.io/ai-news-radar/" style="color:#7c3aed;">AI News Radar</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return html


def _build_error_email(error_msg: str) -> str:
    """构建错误通知邮件"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:40px;background:#f3f4f6;font-family:sans-serif;">
    <table width="480" align="center" cellpadding="0" cellspacing="0">
        <tr>
            <td style="background:#ffffff;border-radius:16px;padding:40px;text-align:center;">
                <h1 style="color:#ef4444;font-size:24px;">❌ 数据获取失败</h1>
                <p style="color:#6b7280;font-size:14px;margin:20px 0;">{error_msg}</p>
                <p style="color:#9ca3af;font-size:12px;">请检查网络连接或数据源状态</p>
            </td>
        </tr>
    </table>
</body>
</html>"""


def build_text_summary(data: dict) -> str:
    """构建纯文本摘要（用于邮件标题或日志）"""
    if not data.get("success"):
        return f"[AI雷达] 数据获取失败 - {data.get('error', '')}"
    
    model_count = len(data.get("model_releases", []))
    aibase_count = data.get("total_aibase", 0)
    generated = data.get("generated_at", "")[:10]
    
    return f"[AI雷达] 模型发布日报 {generated} · {model_count} 条模型更新 / AIbase共{aibase_count}条"
