#!/usr/bin/env python3
"""
Social Media Scheduling Automation
Auto-post across platforms
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any


class SocialMediaScheduler:
    def __init__(self):
        self.posts = []
        self.scheduled = []
        
    def create_post(self, content: str, platforms: List[str], 
                    scheduled_time: str = None, media: str = None) -> Dict[str, Any]:
        post = {
            "id": len(self.posts) + 1,
            "content": content,
            "platforms": platforms,
            "scheduled_time": scheduled_time,
            "media": media,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        self.posts.append(post)
        return post
    
    def schedule_post(self, post_id: int, scheduled_time: str) -> bool:
        for post in self.posts:
            if post["id"] == post_id:
                post["scheduled_time"] = scheduled_time
                post["status"] = "scheduled"
                self.scheduled.append(post)
                return True
        return False
    
    def get_pending_posts(self) -> List[Dict]:
        return [p for p in self.scheduled if p["status"] == "scheduled"]
    
    def get_content_calendar(self, days: int = 7) -> Dict[str, List]:
        calendar = {}
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            calendar[date] = []
        for post in self.scheduled:
            if post["scheduled_time"]:
                date = post["scheduled_time"][:10]
                if date in calendar:
                    calendar[date].append(post)
        return calendar
    
    def generate_weekly_content(self, topics: List[str]) -> List[Dict]:
        templates = [
            "💡 Tip: {topic}",
            "Did you know? {topic}",
            "Here's how {topic} can help your business",
            "Common mistake with {topic}: avoid this!",
            "Success story: How {topic} changed everything"
        ]
        posts = []
        for i, topic in enumerate(topics[:5]):
            content = templates[i % len(templates)].format(topic=topic)
            post = self.create_post(content, ["linkedin", "twitter", "facebook"])
            posts.append(post)
        return posts


if __name__ == "__main__":
    scheduler = SocialMediaScheduler()
    
    posts = scheduler.generate_weekly_content([
        "lead capture",
        "email automation",
        "appointment booking",
        "invoice automation",
        "business growth"
    ])
    
    print(f"Generated {len(posts)} posts:")
    for post in posts:
        print(f"  - {post['content'][:50]}...")
