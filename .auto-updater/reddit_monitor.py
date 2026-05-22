"""
Reddit 监测模块 - 监测 r/Outbound 热门帖子
"""
import re
import requests
from datetime import datetime, timedelta
from config import REDDIT_SUBREDDIT, MIN_UPVOTES_FOR_GUIDE, GUIDE_KEYWORDS

class RedditMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })
    
    def get_hot_posts(self, limit=25, time_filter="day"):
        """
        获取热门帖子
        time_filter: hour, day, week, month, year, all
        返回: list of dict [{id, title, content, upvotes, comments, url, created}]
        """
        try:
            # Reddit JSON API (无需认证，有速率限制)
            url = f"https://www.reddit.com/r/{REDDIT_SUBREDDIT}/hot.json?limit={limit}"
            resp = self.session.get(url, timeout=30)
            
            if resp.status_code == 429:
                print("[Reddit] 速率限制，稍后重试")
                return []
            
            resp.raise_for_status()
            data = resp.json()
            
            posts = []
            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                
                # 过滤掉置顶帖和广告
                if post.get("stickied") or post.get("is_promoted"):
                    continue
                
                post_data = {
                    "id": post.get("id"),
                    "title": post.get("title", ""),
                    "content": post.get("selftext", ""),
                    "upvotes": post.get("ups", 0),
                    "comments": post.get("num_comments", 0),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "created_utc": post.get("created_utc", 0),
                    "author": post.get("author", "unknown"),
                    "flair": post.get("link_flair_text", ""),
                    "is_question": self._is_question_post(post.get("title", "")),
                    "is_guide_worthy": self._is_guide_worthy(post)
                }
                
                posts.append(post_data)
            
            return posts
        except Exception as e:
            print(f"[Reddit] 获取帖子失败: {e}")
            return []
    
    def get_new_posts(self, limit=25):
        """
        获取最新帖子
        """
        try:
            url = f"https://www.reddit.com/r/{REDDIT_SUBREDDIT}/new.json?limit={limit}"
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            posts = []
            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                
                if post.get("stickied"):
                    continue
                
                posts.append({
                    "id": post.get("id"),
                    "title": post.get("title", ""),
                    "content": post.get("selftext", ""),
                    "upvotes": post.get("ups", 0),
                    "comments": post.get("num_comments", 0),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "created_utc": post.get("created_utc", 0),
                    "author": post.get("author", "unknown"),
                    "flair": post.get("link_flair_text", ""),
                    "is_question": self._is_question_post(post.get("title", "")),
                    "is_guide_worthy": self._is_guide_worthy(post)
                })
            
            return posts
        except Exception as e:
            print(f"[Reddit] 获取新帖失败: {e}")
            return []
    
    def _is_question_post(self, title):
        """判断是否是求助帖"""
        question_words = ["how", "what", "where", "why", "help", "question", "bug", "issue", "problem", "fix", "?"]
        title_lower = title.lower()
        return any(word in title_lower for word in question_words)
    
    def _is_guide_worthy(self, post):
        """
        判断是否值得生成攻略页面
        标准：upvotes 足够高，或者内容很详细
        """
        upvotes = post.get("ups", 0)
        content = post.get("selftext", "")
        comments = post.get("num_comments", 0)
        
        # 高互动帖子
        if upvotes >= MIN_UPVOTES_FOR_GUIDE:
            return True
        
        # 内容很长的攻略帖
        if len(content) > 1000 and upvotes >= 5:
            return True
        
        # 高评论数的讨论帖
        if comments >= 20 and upvotes >= 5:
            return True
        
        return False
    
    def classify_content(self, title, content):
        """
        根据关键词分类内容类型
        返回: str 类别 或 None
        """
        text = f"{title} {content}".lower()
        
        scores = {}
        for category, keywords in GUIDE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return None
        
        # 返回得分最高的类别
        return max(scores, key=scores.get)
    
    def extract_guide_content(self, post):
        """
        从帖子中提取攻略内容
        返回: dict {title, summary, tips, category}
        """
        title = post["title"]
        content = post["content"]
        
        # 分类
        category = self.classify_content(title, content)
        
        # 提取要点（简单实现）
        tips = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # 找 bullet points 或数字列表
            if re.match(r'^[\*\-\+•]\s+|^\d+[\.\)]\s+', line):
                if len(line) > 10:  # 过滤太短的
                    tips.append(line)
        
        # 如果没有 bullet points，尝试分段
        if not tips and len(content) > 100:
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
            tips = paragraphs[:5]  # 取前5段
        
        return {
            "title": title,
            "summary": content[:500] + "..." if len(content) > 500 else content,
            "tips": tips[:10],  # 最多10条
            "category": category or "general",
            "source_url": post["url"],
            "upvotes": post["upvotes"],
            "author": post["author"]
        }
