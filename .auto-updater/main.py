"""
Outbound Guide 自动更新系统 - 主程序
每天自动监测 Steam 和 Reddit，发现新内容后自动生成页面
"""
import os
import sys
import subprocess
from datetime import datetime

from config import SITE_REPO_PATH
from state_manager import StateManager
from steam_monitor import SteamMonitor
from reddit_monitor import RedditMonitor
from page_generator import PageGenerator

class OutboundAutoUpdater:
    def __init__(self):
        self.state = StateManager()
        self.steam = SteamMonitor()
        self.reddit = RedditMonitor()
        self.generator = PageGenerator()
        self.report = []
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.report.append(log_msg)
    
    def check_steam_patches(self):
        """检查 Steam 补丁更新"""
        self.log("=" * 50)
        self.log("检查 Steam 补丁...")
        
        patches = self.steam.get_patch_notes()
        if not patches:
            self.log("  未获取到补丁信息")
            return
        
        latest_patch = patches[0]
        current_version = self.state.get_last_patch()
        
        self.log(f"  最新补丁: {latest_patch['version']} ({latest_patch['date']})")
        self.log(f"  本地记录: {current_version or 'None'}")
        
        if latest_patch['version'] != current_version:
            self.log(f"  ✓ 发现新版本: {latest_patch['version']}")
            
            # 生成补丁页面
            filepath = self.generator.generate_patch_notes_page(patches, 'en')
            if filepath:
                self.state.set_last_patch(latest_patch['version'])
                self.state.add_generated_page(
                    "patch_notes",
                    f"Patch {latest_patch['version']}",
                    os.path.basename(filepath)
                )
                self.log(f"  ✓ 生成页面: {os.path.basename(filepath)}")
        else:
            self.log("  → 版本已是最新")
    
    def check_steam_reviews(self):
        """检查 Steam 评价变化"""
        self.log("=" * 50)
        self.log("检查 Steam 评价...")
        
        stats = self.steam.get_review_stats()
        if not stats:
            self.log("  未获取到评价数据")
            return
        
        last_count, last_percent = self.state.get_review_stats()
        current_count = stats['total']
        current_percent = stats['percent']
        
        self.log(f"  当前评价: {current_count} ({current_percent}% positive)")
        self.log(f"  上次记录: {last_count} ({last_percent}% positive)")
        
        # 评价数变化超过阈值才更新
        if abs(current_count - last_count) >= 50:
            self.log(f"  ✓ 评价数变化: {current_count - last_count:+d}")
            self.generator.update_index_stats(current_count, current_percent)
            self.state.set_review_stats(current_count, current_percent)
            self.log("  ✓ 已更新首页数据")
        else:
            self.log("  → 变化较小，跳过更新")
    
    def check_reddit_posts(self):
        """检查 Reddit 热门帖子"""
        self.log("=" * 50)
        self.log("检查 Reddit r/Outbound...")
        
        posts = self.reddit.get_hot_posts(limit=25)
        if not posts:
            self.log("  未获取到帖子")
            return
        
        processed = self.state.get_processed_reddit_posts()
        processed_ids = {p['id'] for p in processed}
        
        new_guides = 0
        for post in posts:
            if post['id'] in processed_ids:
                continue
            
            if post['is_guide_worthy']:
                self.log(f"  ✓ 发现优质帖子: {post['title'][:50]}...")
                self.log(f"    Upvotes: {post['upvotes']}, Comments: {post['comments']}")
                
                # 提取攻略内容
                guide_data = self.reddit.extract_guide_content(post)
                
                # 生成页面
                filepath = self.generator.generate_reddit_guide_page(guide_data, 'en')
                if filepath:
                    self.state.add_processed_reddit_post(post['id'], post['title'])
                    self.state.add_generated_page(
                        "reddit_guide",
                        post['title'],
                        os.path.basename(filepath)
                    )
                    new_guides += 1
                    self.log(f"    → 生成: {os.path.basename(filepath)}")
            else:
                # 记录已处理但不需要生成页面的帖子
                self.state.add_processed_reddit_post(post['id'], post['title'])
        
        if new_guides == 0:
            self.log("  → 没有新的优质攻略帖")
        else:
            self.log(f"  ✓ 共生成 {new_guides} 个新页面")
    
    def git_commit_and_push(self):
        """提交并推送更改"""
        self.log("=" * 50)
        self.log("提交更改到 Git...")
        
        generated = self.generator.get_generated_files()
        if not generated:
            self.log("  → 没有新文件需要提交")
            return
        
        try:
            os.chdir(SITE_REPO_PATH)
            
            # 检查是否有更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if not result.stdout.strip():
                self.log("  → 工作区干净，无需提交")
                return
            
            # 添加所有更改
            subprocess.run(['git', 'add', '-A'], check=True)
            
            # 提交
            commit_msg = f"auto: daily content update {datetime.now().strftime('%Y-%m-%d')}\n\n"
            commit_msg += "Generated pages:\n"
            for f in generated:
                commit_msg += f"- {os.path.basename(f)}\n"
            
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # 推送
            subprocess.run(['git', 'push'], check=True)
            
            self.log("  ✓ 已推送到 GitHub")
            
        except subprocess.CalledProcessError as e:
            self.log(f"  ✗ Git 操作失败: {e}")
        except Exception as e:
            self.log(f"  ✗ 错误: {e}")
    
    def generate_report(self):
        """生成执行报告"""
        self.log("=" * 50)
        self.log("执行完成!")
        
        report_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report))
        
        self.log(f"报告已保存: {report_path}")
    
    def run(self):
        """运行完整流程"""
        self.log("=" * 50)
        self.log("Outbound Guide 自动更新系统")
        self.log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 50)
        
        try:
            # 1. 检查 Steam 补丁
            self.check_steam_patches()
            
            # 2. 检查 Steam 评价
            self.check_steam_reviews()
            
            # 3. 检查 Reddit
            self.check_reddit_posts()
            
            # 4. 提交更改
            self.git_commit_and_push()
            
            # 5. 保存状态
            self.state.save()
            
        except Exception as e:
            self.log(f"✗ 执行出错: {e}")
            import traceback
            self.log(traceback.format_exc())
        
        finally:
            self.generate_report()


def main():
    """主入口"""
    updater = OutboundAutoUpdater()
    updater.run()


if __name__ == "__main__":
    main()
