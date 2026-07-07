"""
数据抓取模块 - 从 AI News Radar 获取 AIbase 最新模型发布信息
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

# AI News Radar 数据源
DATA_URL = "https://raw.githubusercontent.com/LearnPrompt/ai-news-radar/master/data/latest-24h.json"

# AIbase 的 site_id
AIBASE_SITE_ID = "aibase"

# 模型发布相关标签（可以根据需要扩展）
# model_release: 模型发布 | ai_tech: 技术突破 | ai_product_update: 产品更新
MODEL_RELEASE_LABELS = {"model_release", "ai_tech"}


def fetch_raw_data(url: str = DATA_URL) -> Optional[dict]:
    """
    从 AI News Radar 仓库获取最新的 24h JSON 数据
    """
    try:
        logger.info(f"正在获取数据: {url}")
        with urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        logger.info(f"数据获取成功，共 {data.get('total_items', 0)} 条信号")
        return data
    except URLError as e:
        logger.error(f"网络请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {e}")
        return None
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None


def filter_aibase_items(data: dict) -> list:
    """
    从全量数据中筛选出 AIbase 来源的条目
    
    返回按发布时间降序排列的列表
    """
    items = data.get("items", [])
    aibase_items = [
        item for item in items
        if item.get("site_id") == AIBASE_SITE_ID
    ]
    
    # 按发布时间排序（无时间的放后面）
    def sort_key(item):
        pub_time = item.get("published_at")
        if pub_time:
            try:
                return datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return datetime.min.replace(tzinfo=timezone.utc)
        return datetime.min.replace(tzinfo=timezone.utc)
    
    aibase_items.sort(key=sort_key, reverse=True)
    return aibase_items


def filter_model_releases(items: list) -> list:
    """
    从 AIbase 条目中筛选出模型发布/更新相关的内容
    
    策略：
    1. 优先筛选 ai_label 为 model_release 的条目
    2. 同时包含 ai_tech（技术发布）和 ai_product_update（产品更新）
    
    返回筛选后的列表
    """
    model_items = [
        item for item in items
        if item.get("ai_label") in MODEL_RELEASE_LABELS
    ]
    
    # 如果没有 model_release 标签的条目，返回全部 AIbase 条目作为兜底
    if not model_items:
        logger.warning("未找到带 model_release 标签的条目，返回全部 AIbase 条目")
        return items
    
    return model_items


def get_model_releases() -> dict:
    """
    一站式获取 AIbase 模型发布信息
    
    返回结构：
    {
        "success": bool,
        "generated_at": str,       # 数据生成时间
        "fetched_at": str,         # 抓取时间
        "total_aibase": int,       # AIbase 总条目数
        "model_releases": list,    # 模型发布条目列表
        "all_aibase": list,        # AIbase 全部条目（供参考）
        "site_stats": dict,        # 站点统计
    }
    """
    raw_data = fetch_raw_data()
    if not raw_data:
        return {
            "success": False,
            "error": "无法获取数据",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    
    aibase_items = filter_aibase_items(raw_data)
    model_items = filter_model_releases(aibase_items)
    
    # 提取站点统计中的 AIbase 信息
    site_stats = {}
    for stat in raw_data.get("site_stats", []):
        if stat.get("site_id") == AIBASE_SITE_ID:
            site_stats = stat
            break
    
    return {
        "success": True,
        "generated_at": raw_data.get("generated_at", "未知"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_items": raw_data.get("total_items", 0),
        "total_aibase": len(aibase_items),
        "model_releases": model_items,
        "all_aibase": aibase_items,
        "site_stats": site_stats,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = get_model_releases()
    if result["success"]:
        print(f"✅ 数据获取成功")
        print(f"   数据生成时间: {result['generated_at']}")
        print(f"   AIbase 总条目: {result['total_aibase']}")
        print(f"   模型发布相关: {len(result['model_releases'])} 条")
        print()
        for item in result["model_releases"]:
            print(f"  🔸 {item.get('title_zh', '无标题')}")
            print(f"     链接: {item.get('url', '无链接')}")
            print(f"     标签: {item.get('ai_label', '无标签')}")
            print()
    else:
        print(f"❌ 获取失败: {result.get('error')}")
