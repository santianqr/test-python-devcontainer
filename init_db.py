#!/usr/bin/env python3
"""Initialize database for WhatsApp AI Assistant."""

import sys
import time

from dotenv import load_dotenv

from database import init_database, test_connection
from vector_store import BusinessKnowledgeStore, init_sample_knowledge

load_dotenv()


def check_postgres() -> bool:
    """Check if PostgreSQL is ready."""
    print("🔍 Checking PostgreSQL connection...")

    for attempt in range(10):
        try:
            result = test_connection()
            if result["status"] == "connected":
                print(f"✅ PostgreSQL connected: {result['current_time']}")
                return True
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/10: {e}")
            time.sleep(2)

    print("❌ PostgreSQL not available")
    return False


def init_all() -> bool:
    """Initialize database, tables, and sample data."""
    try:
        print("🔄 Creating tables...")
        init_database()
        print("✅ Tables created")

        print("🔄 Setting up vector store...")
        store = BusinessKnowledgeStore()
        store.setup_vector_extension()
        print("✅ Vector store ready")

        print("🔄 Adding sample data...")
        init_sample_knowledge()
        print("✅ Sample data added")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_data() -> bool:
    """Verify data was inserted correctly."""
    try:
        print("🔍 Verifying data...")
        from database import get_session

        session = get_session()

        from sqlalchemy import text

        conv_count = session.execute(text("SELECT COUNT(*) FROM conversations")).fetchone()[0]
        print(f"📊 Conversations: {conv_count} records")

        bk_count = session.execute(text("SELECT COUNT(*) FROM business_knowledge")).fetchone()[0]
        print(f"📊 Business knowledge: {bk_count} records")

        session.close()
        return bk_count > 0
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Database Initialization")
    print("=" * 30)

    if not check_postgres():
        print("\n💡 Start PostgreSQL first:")
        print("   docker-compose up -d")
        return 1

    if not init_all():
        return 1

    if not verify_data():
        print("⚠️  Data verification failed")
        return 1

    print("\n🎉 Database ready!")
    print("   Run: uv run python main.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
