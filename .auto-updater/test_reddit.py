from reddit_monitor import RedditMonitor

r = RedditMonitor()
posts = r.get_hot_posts(limit=5)

for p in posts[:3]:
    print(f"{p['upvotes']:3d} ↑ | {p['title'][:50]}... | GuideWorthy: {p['is_guide_worthy']}")
