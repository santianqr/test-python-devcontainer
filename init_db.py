#!/usr/bin/env python3
"""Initialize database for WhatsApp AI Assistant."""

import sys
import time

from dotenv import load_dotenv

from database import init_database, test_connection
from vector_store import BusinessKnowledgeStore, init_sample_knowledge

# Load environment variables
load_dotenv()


def wait_for_postgres(max_attempts: int = 30) -> bool:
    """Wait for PostgreSQL to be ready."""
    print("🔄 Waiting for PostgreSQL to be ready...")

    for attempt in range(max_attempts):
        try:
            result = test_connection()
            if result["status"] == "connected":
                print(f"✅ PostgreSQL is ready! Connected at: {result['current_time']}")
                return True
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}: PostgreSQL not ready yet - {e}")
            time.sleep(2)

    print("❌ PostgreSQL failed to become ready in time")
    return False


def setup_vector_store() -> bool:
    """Setup vector store with extensions and indexes."""
    print("🔄 Setting up vector store...")

    try:
        store = BusinessKnowledgeStore()

        # Setup pgvector extension
        if store.setup_vector_extension():
            print("✅ pgvector extension enabled")
        else:
            print("⚠️  Warning: Could not enable pgvector extension")
            return False

        # Note: We'll create the vector index later when we have data
        # This is because IVFFlat indexes need data to train on
        print("ℹ️  Vector index will be created after adding sample data")

        return True
    except Exception as e:
        print(f"❌ Error setting up vector store: {e}")
        return False


def initialize_sample_data() -> bool:
    """Initialize with sample business knowledge."""
    print("🔄 Adding sample business knowledge...")

    try:
        init_sample_knowledge()
        print("✅ Sample business knowledge added")

        # Now try to create the vector index
        store = BusinessKnowledgeStore()
        if store.create_vector_index():
            print("✅ Vector index created")
        else:
            print("⚠️  Warning: Could not create vector index (this is normal if you have less than 1000 vectors)")

        return True
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False


def main() -> int:
    """Main initialization function."""
    print("🚀 Starting WhatsApp AI Assistant Database Initialization")
    print("=" * 60)

    # Step 1: Wait for PostgreSQL
    if not wait_for_postgres():
        print("❌ Database initialization failed: PostgreSQL not available")
        return 1

    # Step 2: Initialize database tables
    print("🔄 Creating database tables...")
    try:
        init_database()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return 1

    # Step 3: Setup vector store
    if not setup_vector_store():
        print("❌ Vector store setup failed")
        return 1

    # Step 4: Add sample data
    if not initialize_sample_data():
        print("❌ Sample data initialization failed")
        return 1

    # Step 5: Final connection test
    print("🔄 Running final connection test...")
    try:
        result = test_connection()
        if result["status"] == "connected":
            print("✅ Final connection test passed")
            print(f"📊 Database: {result.get('database', 'Unknown')}")
            print(f"🕒 Current time: {result.get('current_time', 'Unknown')}")
        else:
            print(f"❌ Final connection test failed: {result}")
            return 1
    except Exception as e:
        print(f"❌ Final connection test error: {e}")
        return 1

    print("=" * 60)
    print("🎉 Database initialization completed successfully!")
    print("")
    print("Next steps:")
    print("1. Update your .env file with your OpenAI API key")
    print("2. Run: uv run python main.py")
    print("3. Visit: http://localhost:8000/docs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
