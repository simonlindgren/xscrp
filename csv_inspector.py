#!/usr/bin/env python3
import pandas as pd

def inspect_csv():
    # Get CSV filename from user
    filename = input("csv file to inspect >> ").strip()
    
    try:
        # Load data
        data = pd.read_csv(filename)
        
        # Data overview and statistics
        print(f"total posts: {len(data):,}")
        print()

        # Convert date column to datetime if it exists
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            
            print(f"start: {data['date'].min()}")
            print(f"end: {data['date'].max()}")
            print(f"span: {(data['date'].max() - data['date'].min()).days + 1} days")
            print()
            
            # Posts per day
            daily_counts = data['date'].dt.date.value_counts().sort_index()
            print(f"avg posts per day: {daily_counts.mean():.1f}")
            print(f"max posts per day: {daily_counts.max()}")
            print(f"min posts per day: {daily_counts.min()}")
            print()

        # User statistics
        if 'username' in data.columns:
            print("users")
            unique_users = data['username'].nunique()
            print(f"unique: {unique_users:,}")
            print(f"avg posts per user: {len(data) / unique_users:.1f}")
            
            top_users = data['username'].value_counts().head()
            print("top 5 active:")
            for user, count in top_users.items():
                print(f"  @{user}: {count}")
            print()

        # Engagement statistics
        engagement_cols = ['likes', 'retweets', 'replies']
        available_engagement = [col for col in engagement_cols if col in data.columns]

        if available_engagement:
            print("engagement")
            for col in available_engagement:
                print(f"{col}:")
                print(f"  total: {data[col].sum():,}")
                print(f"  avg: {data[col].mean():.1f}")
                print(f"  median: {data[col].median():.1f}")
                print(f"  max: {data[col].max():,}")
            print()
            
    except FileNotFoundError:
        print(f"❌ file '{filename}' not found")
    except Exception as e:
        print(f"❌ error reading file: {e}")

if __name__ == "__main__":
    inspect_csv()
