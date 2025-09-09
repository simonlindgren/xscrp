#!/usr/bin/env python3
import asyncio
from twscrape import API

async def check_accounts():
    api = API()
    
    accounts = await api.pool.accounts_info()
    
    print("=== ACCOUNT STATUS ===")
    print(f"Total accounts: {len(accounts)}")
    print()
    
    for account in accounts:
        status = "ACTIVE" if account.active else "INACTIVE"
        print(f"@{account.username} ({account.email}) - {status}")
        
        if hasattr(account, 'locks') and account.locks:
            print(f"  Rate limits: {account.locks}")
        
        print()

if __name__ == "__main__":
    asyncio.run(check_accounts())
