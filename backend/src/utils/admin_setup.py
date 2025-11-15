"""
Admin Setup Utility
Run this script to register an admin user
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.admin import Admin


async def register_admin():
    """Register a new admin"""
    print("\n🔐 OTT Bot - Admin Registration\n")
    
    # Load environment
    load_dotenv()
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'test_database')
    
    # Connect to database
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    admins_collection = db['admins']
    
    # Get admin details
    print("Enter admin Telegram ID (numeric ID from Telegram):")
    telegram_id = input("> ").strip()
    
    if not telegram_id.isdigit():
        print("❌ Invalid Telegram ID. Must be numeric.")
        return
    
    telegram_id = int(telegram_id)
    
    print("\nEnter admin username (optional, press Enter to skip):")
    username = input("> ").strip() or None
    
    print("\nEnter admin first name (optional, press Enter to skip):")
    first_name = input("> ").strip() or None
    
    # Check if admin already exists
    existing_admin = await admins_collection.find_one({"telegram_id": telegram_id})
    
    if existing_admin:
        print(f"\n⚠️  Admin with Telegram ID {telegram_id} already exists!")
        print("Do you want to reactivate? (y/n):")
        choice = input("> ").strip().lower()
        
        if choice == 'y':
            await admins_collection.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"is_active": True}}
            )
            print("\n✅ Admin reactivated successfully!")
        return
    
    # Create new admin
    admin = Admin(
        telegram_id=telegram_id,
        telegram_username=username,
        first_name=first_name
    )
    
    await admins_collection.insert_one(admin.model_dump())
    
    print("\n✅ Admin registered successfully!")
    print(f"\n📋 Admin Details:")
    print(f"   Telegram ID: {telegram_id}")
    print(f"   Username: @{username}" if username else "   Username: Not set")
    print(f"   First Name: {first_name}" if first_name else "   First Name: Not set")
    print(f"\n💡 This user can now access the Admin Panel in the bot.")
    
    client.close()


async def list_admins():
    """List all admins"""
    print("\n👑 Current Admins\n")
    
    load_dotenv()
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    admins_collection = db['admins']
    
    admins = await admins_collection.find({}).to_list(length=100)
    
    if not admins:
        print("No admins registered yet.")
        client.close()
        return
    
    for i, admin in enumerate(admins, 1):
        status = "🟢 Active" if admin.get('is_active') else "🔴 Inactive"
        print(f"{i}. {status}")
        print(f"   Telegram ID: {admin['telegram_id']}")
        print(f"   Username: @{admin.get('telegram_username', 'N/A')}")
        print(f"   First Name: {admin.get('first_name', 'N/A')}")
        print()
    
    client.close()


async def main():
    """Main menu"""
    print("\n" + "="*50)
    print("🤖 OTT Subscription Bot - Admin Management")
    print("="*50)
    
    print("\nWhat would you like to do?")
    print("1. Register new admin")
    print("2. List all admins")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        await register_admin()
    elif choice == "2":
        await list_admins()
    elif choice == "3":
        print("\nGoodbye! 👋")
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
