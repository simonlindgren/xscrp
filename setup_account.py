#!/usr/bin/env python3
"""Minimal account setup for twscrape."""

import asyncio
import getpass
from twscrape import API

async def setup():
    print("add x account")
    print("=" * 30)
    
    username = input("x username: ").strip()
    password = getpass.getpass("x password: ").strip()
    email = input("email: ").strip()

    print("\ncookies (from browser - recommended):")
    print("Example: auth_token=abc123; ct0=def456")
    cookies = input("cookies (or press Enter to skip): ").strip()
    
    api = API()
    
    try:
        if cookies:
            await api.pool.add_account(username, password, email, "dummy", cookies=cookies)
            print(f"✅ Added {username} with cookies")
        else:
            await api.pool.add_account(username, password, email, "dummy")
            print(f"✅ Added {username}")
            await api.pool.login_all()
            print("✅ Login completed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(setup())
