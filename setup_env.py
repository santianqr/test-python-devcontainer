#!/usr/bin/env python3
"""Interactive setup script for WhatsApp AI Assistant environment."""

import os
import shutil
from pathlib import Path


def create_env_file():
    """Create .env file from template."""
    env_example = Path("env_example")
    env_file = Path(".env")

    if env_file.exists():
        response = input("🔄 .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("ℹ️  Keeping existing .env file")
            return False

    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        return True
    else:
        print("❌ env_example file not found")
        return False


def setup_openai_key():
    """Interactive OpenAI API key setup."""
    env_file = Path(".env")

    if not env_file.exists():
        print("❌ .env file not found. Run create_env_file() first.")
        return False

    print("\n🔑 OpenAI API Key Setup")
    print("=" * 40)
    print("You need an OpenAI API key to use this assistant.")
    print("Get one at: https://platform.openai.com/api-keys")
    print("")

    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()

    if not api_key:
        print("⏭️  Skipping OpenAI API key setup")
        print("⚠️  Remember to add it to .env later: OPENAI_API_KEY=your_key_here")
        return False

    # Read current .env content
    content = env_file.read_text()

    # Replace the placeholder
    updated_content = content.replace("OPENAI_API_KEY=your_openai_api_key_here", f"OPENAI_API_KEY={api_key}")

    # Write back
    env_file.write_text(updated_content)
    print("✅ OpenAI API key added to .env file")
    return True


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")

    # Check if we're in a devcontainer
    if os.path.exists("/.devcontainer"):
        print("✅ Running in devcontainer")
    else:
        print("⚠️  Not running in devcontainer (this is OK for local development)")

    # Check if PostgreSQL is accessible
    try:
        import psycopg2

        print("✅ psycopg2 (PostgreSQL driver) is available")
    except ImportError:
        print("❌ psycopg2 not found. Run: uv sync --extra dev --extra ds")
        return False

    # Check if required packages are available
    try:
        import fastapi
        import langchain
        import openai

        print("✅ Core packages are available")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        return False

    return True


def main():
    """Main setup function."""
    print("🚀 WhatsApp AI Assistant - Environment Setup")
    print("=" * 50)

    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install dependencies first:")
        print("   uv sync --extra dev --extra ds")
        return

    # Step 2: Create .env file
    print("\n📄 Environment File Setup")
    print("-" * 30)
    create_env_file()

    # Step 3: Setup OpenAI key
    setup_openai_key()

    # Step 4: Instructions
    print("\n🎯 Next Steps")
    print("-" * 20)
    print("1. 🐳 If using devcontainer, rebuild it to get PostgreSQL")
    print("2. 🗄️  Initialize database: uv run python init_db.py")
    print("3. 🚀 Start the application: uv run python main.py")
    print("4. 🌐 Visit: http://localhost:8000/docs")
    print("")
    print("💡 Tip: The database is automatically configured for localhost PostgreSQL")
    print("   No additional database setup needed!")


if __name__ == "__main__":
    main()
