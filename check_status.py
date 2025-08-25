#!/usr/bin/env python3
"""Check the complete status of the WhatsApp AI Assistant system."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """Check environment configuration."""
    print("🔍 Environment Configuration")
    print("-" * 30)

    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")

        # Check key environment variables
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            print("✅ OpenAI API key configured")
        else:
            print("⚠️  OpenAI API key not configured")

        db_url = os.getenv("DATABASE_URL")
        if db_url:
            print(f"✅ Database URL: {db_url}")
        else:
            print("⚠️  DATABASE_URL not set")
    else:
        print("❌ .env file not found")


def check_database():
    """Check database connection and structure."""
    print("\n🗄️  Database Status")
    print("-" * 20)

    try:
        from database import test_connection

        result = test_connection()

        if result["status"] == "connected":
            print("✅ PostgreSQL connected")
            print(f"   Time: {result.get('current_time', 'Unknown')}")
            print(f"   Database: {result.get('database', 'Unknown')}")
        else:
            print(f"❌ Database error: {result}")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # Check tables
    try:
        from database import get_session

        session = get_session()

        # Check conversations table
        result = session.execute("SELECT COUNT(*) FROM conversations").fetchone()
        print(f"✅ Conversations table: {result[0]} records")

        # Check business_knowledge table
        result = session.execute("SELECT COUNT(*) FROM business_knowledge").fetchone()
        print(f"✅ Business knowledge table: {result[0]} records")

        # Check pgvector extension
        result = session.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'").fetchone()
        if result:
            print("✅ pgvector extension enabled")
        else:
            print("⚠️  pgvector extension not found")

        session.close()
        return True
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False


def check_vector_store():
    """Check vector store functionality."""
    print("\n🔍 Vector Store Status")
    print("-" * 22)

    try:
        from vector_store import BusinessKnowledgeStore

        store = BusinessKnowledgeStore()

        # Try a sample search
        results = store.search_knowledge("información sobre la empresa", limit=2)
        if results:
            print(f"✅ Vector search working: {len(results)} results")
            print(f"   Sample: {results[0]['content'][:50]}...")
        else:
            print("⚠️  No vector search results (may need sample data)")

        return True
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False


def check_openai():
    """Check OpenAI connectivity."""
    print("\n🤖 OpenAI Status")
    print("-" * 16)

    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # Simple test
        response = llm.invoke("Say 'OpenAI connection test passed'")
        if "test passed" in response.content.lower():
            print("✅ OpenAI chat model working")
        else:
            print("⚠️  OpenAI responded but content unexpected")

        return True
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False


def main():
    """Run complete system check."""
    print("🏥 WhatsApp AI Assistant - System Health Check")
    print("=" * 50)

    checks = [
        check_environment(),
        check_database(),
        check_vector_store(),
        check_openai(),
    ]

    passed = sum(1 for check in checks if check is not False)
    total = len(checks)

    print("\n" + "=" * 50)
    print(f"📊 Health Check Summary: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All systems operational!")
        print("🚀 Ready to run: uv run python main.py")
    else:
        print("⚠️  Some issues detected. Check logs above.")

        if not check_environment():
            print("💡 Run: uv run python setup_env.py")
        if not check_database():
            print("💡 Run: uv run python init_db.py")


if __name__ == "__main__":
    main()
