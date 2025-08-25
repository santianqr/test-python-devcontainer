#!/usr/bin/env python3
"""Complete initialization script that combines environment setup and database initialization."""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} failed: Command not found")
        return False


def check_env_file() -> bool:
    """Check if .env file exists and has OpenAI key."""
    env_file = Path(".env")

    if not env_file.exists():
        print("⚠️  .env file not found")
        return False

    content = env_file.read_text()
    if "your_openai_api_key_here" in content:
        print("⚠️  OpenAI API key not configured in .env")
        return False

    print("✅ .env file configured")
    return True


def main():
    """Main initialization function."""
    print("🚀 WhatsApp AI Assistant - Complete Setup")
    print("=" * 50)

    # Step 1: Environment setup
    print("\n📄 Step 1: Environment Setup")
    print("-" * 30)

    if not run_command([sys.executable, "setup_env.py"], "Environment setup"):
        print("❌ Environment setup failed")
        return 1

    # Step 2: Check environment configuration
    if not check_env_file():
        print("\n⚠️  Warning: .env file may need manual configuration")
        print("   Edit .env and add your OpenAI API key")
        print("   Then run: uv run python init_db.py")
        return 0

    # Step 3: Database initialization
    print("\n🗄️  Step 2: Database Initialization")
    print("-" * 35)

    if not run_command([sys.executable, "init_db.py"], "Database initialization"):
        print("❌ Database initialization failed")
        return 1

    # Step 4: Success message
    print("\n" + "=" * 50)
    print("🎉 Complete setup finished successfully!")
    print("")
    print("🚀 Ready to start the application:")
    print("   uv run python main.py")
    print("")
    print("🌐 Then visit:")
    print("   http://localhost:8000/docs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
