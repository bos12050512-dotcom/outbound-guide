"""
Outbound Guide 自动更新系统配置
"""
import os

# Steam 配置
STEAM_APP_ID = 2681030
STEAM_NEWS_URL = f"https://steamcommunity.com/app/{STEAM_APP_ID}/allnews/"
STEAM_STORE_URL = f"https://store.steampowered.com/app/{STEAM_APP_ID}/"

# Reddit 配置
REDDIT_SUBREDDIT = "Outbound"
REDDIT_USER_AGENT = "OutboundGuideBot/1.0"

# 网站项目路径
SITE_REPO_PATH = os.environ.get("SITE_REPO_PATH", r"C:\Users\OASIS\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a0d91f290dfe4c370d6c29e\outbound-site")

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 状态文件
STATE_FILE = os.path.join(DATA_DIR, "monitor_state.json")

# 更新阈值
MIN_UPVOTES_FOR_GUIDE = 10  # Reddit 帖子最少 upvotes 才生成攻略
MIN_REVIEWS_CHANGE = 50     # 评价数变化超过此值才更新首页

# 内容分类关键词
GUIDE_KEYWORDS = {
    "starter": ["新手", "开荒", "开始", "入门", "first hour", "beginner", "starter", "new player"],
    "crafting": ["合成", "配方", "制作", "craft", "recipe", "blueprint"],
    "energy": ["电力", "能源", "电池", "太阳能", "energy", "power", "battery", "solar"],
    "van": ["房车", "升级", "布局", "van", "upgrade", "layout", "module"],
    "multiplayer": ["联机", "多人", "合作", "multiplayer", "co-op", "coop", "online"],
    "collectibles": ["收集", "隐藏", "秘密", "collectible", "secret", "hidden", "usb", "cairn"],
    "progression": ["科技树", "进度", "解锁", "progression", "tech tree", "unlock"],
    "items": ["物品", "资源", "材料", "item", "resource", "material", "redwood", "gnome"],
    "fixes": ["修复", "bug", "错误", "fix", "bugfix", "crash", "error", "il2cpp"],
    "achievements": ["成就", "achievement", "trophy"],
}

# 页面模板配置
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
