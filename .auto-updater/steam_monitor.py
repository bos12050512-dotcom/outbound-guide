"""
Steam 监测模块 - 监测补丁、新闻、评价
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import STEAM_APP_ID, STEAM_NEWS_URL, STEAM_STORE_URL

class SteamMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_patch_notes(self):
        """
        获取 Steam 社区的最新补丁说明
        返回: list of dict [{version, title, date, content, url}]
        """
        try:
            resp = self.session.get(STEAM_NEWS_URL, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            patches = []
            news_items = soup.find_all('div', class_='apphub_Card')
            
            for item in news_items[:10]:  # 只取前10条
                title_elem = item.find('div', class_='apphub_CardContentTitle')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 识别补丁标题 (通常包含 "Update" 或版本号)
                patch_match = re.search(r'Update\s+(\d+\.\d+\.?\d*)', title, re.I)
                if not patch_match:
                    patch_match = re.search(r'(\d+\.\d+\.?\d*)', title)
                
                if patch_match:
                    version = patch_match.group(1)
                    
                    # 获取日期
                    date_elem = item.find('div', class_='apphub_CardContentDate')
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # 获取链接
                    link_elem = item.find('a', href=True)
                    url = link_elem['href'] if link_elem else ""
                    
                    # 获取内容预览
                    content_elem = item.find('div', class_='apphub_CardTextContent')
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    patches.append({
                        "version": version,
                        "title": title,
                        "date": date_str,
                        "content_preview": content[:500],
                        "url": url
                    })
            
            return patches
        except Exception as e:
            print(f"[Steam] 获取补丁失败: {e}")
            return []
    
    def get_news(self):
        """
        获取非补丁类新闻
        返回: list of dict [{title, date, content, url}]
        """
        try:
            resp = self.session.get(STEAM_NEWS_URL, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            news = []
            news_items = soup.find_all('div', class_='apphub_Card')
            
            for item in news_items[:5]:
                title_elem = item.find('div', class_='apphub_CardContentTitle')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 跳过补丁类
                if re.search(r'update|patch|hotfix', title, re.I):
                    continue
                
                date_elem = item.find('div', class_='apphub_CardContentDate')
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                
                link_elem = item.find('a', href=True)
                url = link_elem['href'] if link_elem else ""
                
                content_elem = item.find('div', class_='apphub_CardTextContent')
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                news.append({
                    "title": title,
                    "date": date_str,
                    "content": content[:800],
                    "url": url
                })
            
            return news
        except Exception as e:
            print(f"[Steam] 获取新闻失败: {e}")
            return []
    
    def get_review_stats(self):
        """
        获取 Steam 评价统计
        返回: dict {total, positive, negative, percent}
        """
        try:
            # 使用 Steam API 获取评价
            api_url = f"https://store.steampowered.com/appreviews/{STEAM_APP_ID}?json=1&language=all"
            resp = self.session.get(api_url, timeout=30)
            data = resp.json()
            
            if data.get("success") == 1:
                summary = data.get("query_summary", {})
                total = summary.get("total_reviews", 0)
                positive = summary.get("total_positive", 0)
                negative = summary.get("total_negative", 0)
                percent = round(positive / total * 100, 1) if total > 0 else 0
                
                return {
                    "total": total,
                    "positive": positive,
                    "negative": negative,
                    "percent": percent
                }
        except Exception as e:
            print(f"[Steam] 获取评价失败: {e}")
        
        return None
    
    def get_full_patch_content(self, url):
        """
        获取完整补丁内容
        """
        try:
            resp = self.session.get(url, timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            content_div = soup.find('div', class_='apphub_CardTextContent')
            if content_div:
                return content_div.get_text(separator='\n', strip=True)
            
            return ""
        except Exception as e:
            print(f"[Steam] 获取完整内容失败: {e}")
            return ""
