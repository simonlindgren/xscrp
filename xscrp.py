#!/usr/bin/env python3
"""Minimal Twitter date range search."""

import asyncio
import json
import pandas as pd
import re
from datetime import datetime, timedelta, date
from twscrape import API, gather

class xscrp:
    def __init__(self):
        self.api = API()
    
    def parse_next_available_time(self, error_message):
        """Parse 'Next available at HH:MM:SS' from error message and return seconds to wait"""
        match = re.search(r'Next available at (\d{2}):(\d{2}):(\d{2})', str(error_message))
        if match:
            target_hour, target_min, target_sec = map(int, match.groups())
            now = datetime.now()
            target_time = now.replace(hour=target_hour, minute=target_min, second=target_sec, microsecond=0)
            
            # If target time is in the past, assume it's tomorrow
            if target_time <= now:
                target_time += timedelta(days=1)
            
            wait_seconds = (target_time - now).total_seconds()
            return max(wait_seconds, 60)  # Wait at least 1 minute
        return 300  # Default 5 minutes if we can't parse
    
    def get_date(self, prompt):
        while True:
            date_str = input(prompt).strip()
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("  ---- use format: YYYY-MM-DD\n")
    
    async def search_date_range(self, query, start_date, end_date, daily_limit, archive_name):
        # Create CSV filename with archive name only
        filename = f"{archive_name}.csv"
        
        current = start_date
        day = 0
        total_days = (end_date - start_date).days + 1
        total_tweets = 0
        
        print(f"\n  searching {total_days} days...")
        print(f"  writing to: {filename}")
        
        try:
            while current <= end_date:
                day += 1
                next_day = current + timedelta(days=1)
                daily_query = f"{query} since:{current} until:{next_day}"
                
                print(f"     -- {day}/{total_days}: {current} ", end="", flush=True)
                
                try:
                    tweets = await gather(self.api.search(daily_query, limit=daily_limit))
                    
                    if tweets:
                        valid_tweets = [t for t in tweets if t.date and t.date.date() == current]
                        
                        # Convert to DataFrame and append to CSV
                        if valid_tweets:
                            data = []
                            for tweet in valid_tweets:
                                data.append({
                                    'date': tweet.date.isoformat() if tweet.date else None,
                                    'username': tweet.user.username,
                                    'display_name': getattr(tweet.user, 'displayname', tweet.user.username),
                                    'content': tweet.rawContent,
                                    'likes': tweet.likeCount,
                                    'retweets': tweet.retweetCount,
                                    'replies': tweet.replyCount,
                                    'url': f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"
                                })
                            
                            df = pd.DataFrame(data)
                            # Write header only on first write
                            write_header = not pd.io.common.file_exists(filename)
                            df.to_csv(filename, mode='a', header=write_header, index=False)
                            total_tweets += len(valid_tweets)
                            
                        print(f"--> {len(valid_tweets)} (total: {total_tweets})")
                    else:
                        print("no matching posts found")
                    
                    await asyncio.sleep(1.5)  # Rate limit delay
                    
                except Exception as e:
                    error_str = str(e)
                    if "rate limit" in error_str.lower() or "No account available" in error_str:
                        wait_time = self.parse_next_available_time(error_str)
                        wait_minutes = int(wait_time / 60)
                        print(f"☠️  rate limited - waiting {wait_minutes} minutes...")
                        await asyncio.sleep(wait_time)
                        continue  # Retry the same day
                    else:
                        print(f"❌ {error_str[:50]}...")
                        # Continue to next day on other errors
                
                current += timedelta(days=1)
        
        except KeyboardInterrupt:
            print(f"\nstopped by user after {day} days")
            print(f"total tweets saved: {total_tweets}")
        
        print(f"   final results in: {filename}")
        return filename
    
    def save_results(self, tweets, query, archive_name):
        if not tweets:
            print("❌ No tweets to save")
            return
        
        # Convert to simple format
        data = []
        for tweet in tweets:
            data.append({
                'date': tweet.date.isoformat() if tweet.date else None,
                'username': tweet.user.username,
                'display_name': getattr(tweet.user, 'displayname', tweet.user.username),
                'content': tweet.rawContent,
                'likes': tweet.likeCount,
                'retweets': tweet.retweetCount,
                'replies': tweet.replyCount,
                'url': f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"
            })
        
        # Save as CSV
        df = pd.DataFrame(data)
        filename = f"{archive_name}.csv"
        df.to_csv(filename, index=False)
        
        print(f"💾 Saved {len(data)} tweets to {filename}")

async def main():
    print("""
 ╭─────────────────────────────────────────────╮
 │ ██╗  ██╗ ███████╗  ██████╗ ██████╗ ██████╗  │
 │ ╚██╗██╔╝ ██╔════╝ ██╔════╝ ██╔══██╗██╔══██╗ │
 │  ╚███╔╝  ███████╗ ██║      ██████╔╝██████╔╝ │
 │  ██╔██╗  ╚════██║ ██║      ██╔══██╗██╔═══╝  │
 │ ██╔╝ ██╗ ███████║ ╚██████╗ ██║  ██║██║      │
 │ ╚═╝  ╚═╝ ╚══════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝      │
 │001001010101011110001110001110001101110001101│
 ╰─────────────────────────────────────────────╯
    """)
    
    search = xscrp()
    
    # Get inputs
    query = input("  search query >> ").strip()
    archive_name = input("  archive name >> ").strip()
    start_date = search.get_date("  start date (YYYY-MM-DD) >> ")
    end_date = search.get_date("  end date (YYYY-MM-DD) >> ")
    print("")

    while True:
        try:
            daily_limit = int(input("  tweets per day (default 50, max recommended 500): ") or "50")
            if daily_limit > 500:
                if input(f"  ---- {daily_limit} is more than recommended due to rate limits. still continue? might work... (y/N): ").lower() != 'y':
                    continue
            break
        except ValueError:
            print("   ---- enter a number\n")
    
    # Search
    filename = await search.search_date_range(query, start_date, end_date, daily_limit, archive_name)

if __name__ == "__main__":
    asyncio.run(main())
