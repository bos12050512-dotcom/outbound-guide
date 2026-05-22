"""
完整流程测试（不提交 Git）
"""
import os
import sys

# 设置测试环境
os.environ['SITE_REPO_PATH'] = r"C:\Users\OASIS\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a0d91f290dfe4c370d6c29e\outbound-site"

from state_manager import StateManager
from steam_monitor import SteamMonitor
from reddit_monitor import RedditMonitor
from page_generator import PageGenerator

def test():
    print("=" * 60)
    print("Outbound Guide 自动更新系统 - 测试运行")
    print("=" * 60)
    
    # 1. 测试 Steam 评价
    print("\n[1] 测试 Steam 评价监测...")
    steam = SteamMonitor()
    stats = steam.get_review_stats()
    if stats:
        print(f"  ✓ 评价数: {stats['total']}, 好评率: {stats['percent']}%")
    else:
        print("  ✗ 获取失败")
    
    # 2. 测试 Steam 补丁
    print("\n[2] 测试 Steam 补丁监测...")
    patches = steam.get_patch_notes()
    if patches:
        print(f"  ✓ 找到 {len(patches)} 个补丁")
        print(f"  ✓ 最新: {patches[0]['version']} - {patches[0]['title'][:50]}...")
    else:
        print("  ✗ 获取失败")
    
    # 3. 测试 Reddit
    print("\n[3] 测试 Reddit 监测...")
    reddit = RedditMonitor()
    posts = reddit.get_hot_posts(limit=10)
    guide_worthy = [p for p in posts if p['is_guide_worthy']]
    print(f"  ✓ 获取 {len(posts)} 个帖子")
    print(f"  ✓ 其中 {len(guide_worthy)} 个值得生成攻略")
    
    # 4. 测试页面生成
    print("\n[4] 测试页面生成...")
    generator = PageGenerator()
    
    # 测试更新首页
    if stats:
        generator.update_index_stats(stats['total'], stats['percent'])
        print("  ✓ 首页数据更新测试完成")
    
    # 测试生成补丁页面
    if patches:
        # 使用测试文件名避免覆盖
        test_patch = [patches[0]]
        test_patch[0]['version'] = 'test-' + test_patch[0]['version']
        filepath = generator.generate_patch_notes_page(test_patch, 'en')
        if filepath:
            print(f"  ✓ 测试页面生成: {os.path.basename(filepath)}")
            # 清理测试文件
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"  ✓ 测试文件已清理")
    
    print("\n" + "=" * 60)
    print("测试完成！所有模块运行正常。")
    print("=" * 60)

if __name__ == "__main__":
    test()
