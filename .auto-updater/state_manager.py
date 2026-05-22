"""
状态管理器 - 记录上次监测状态，用于对比变化
"""
import json
import os
from datetime import datetime
from config import STATE_FILE

class StateManager:
    def __init__(self):
        self.state = self._load()
    
    def _load(self):
        """加载状态文件"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_check": None,
            "steam": {
                "last_patch_version": None,
                "last_news_ids": [],
                "review_count": 0,
                "positive_percent": 0
            },
            "reddit": {
                "last_post_ids": [],
                "processed_posts": []
            },
            "generated_pages": []
        }
    
    def save(self):
        """保存状态"""
        self.state["last_check"] = datetime.now().isoformat()
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def get_last_patch(self):
        return self.state["steam"].get("last_patch_version")
    
    def set_last_patch(self, version):
        self.state["steam"]["last_patch_version"] = version
    
    def get_last_news_ids(self):
        return self.state["steam"].get("last_news_ids", [])
    
    def set_last_news_ids(self, ids):
        self.state["steam"]["last_news_ids"] = ids
    
    def get_review_stats(self):
        return (
            self.state["steam"].get("review_count", 0),
            self.state["steam"].get("positive_percent", 0)
        )
    
    def set_review_stats(self, count, percent):
        self.state["steam"]["review_count"] = count
        self.state["steam"]["positive_percent"] = percent
    
    def get_processed_reddit_posts(self):
        return self.state["reddit"].get("processed_posts", [])
    
    def add_processed_reddit_post(self, post_id, title):
        self.state["reddit"].setdefault("processed_posts", []).append({
            "id": post_id,
            "title": title,
            "processed_at": datetime.now().isoformat()
        })
    
    def add_generated_page(self, page_type, title, filename):
        self.state["generated_pages"].append({
            "type": page_type,
            "title": title,
            "filename": filename,
            "generated_at": datetime.now().isoformat()
        })
