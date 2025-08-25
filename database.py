"""Database configuration and models for WhatsApp AI Agent."""

import os
from datetime import datetime

from dotenv import load_dotenv
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Conversation(Base):
    """Model for storing conversation history."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(255), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class BusinessKnowledge(Base):
    """Model for storing business knowledge with vector embeddings."""

    __tablename__ = "business_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding: Vector = Column(Vector(1536), nullable=True)
    meta_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_database_url() -> str:
    """Get database URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("DB_USER") or os.getenv("user")
    password = os.getenv("DB_PASSWORD") or os.getenv("password")
    host = os.getenv("DB_HOST") or os.getenv("host")
    port = os.getenv("DB_PORT") or os.getenv("port")
    dbname = os.getenv("DB_NAME") or os.getenv("dbname")

    if all([user, password, host, port, dbname]):
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    return "postgresql://postgres:postgres123@postgres:5432/whatsapp_ai"


def create_database_engine():
    """Create SQLAlchemy engine with connection pooling."""
    database_url = get_database_url()

    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )
    return engine


def get_session():
    """Get database session."""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_database():
    """Initialize database tables."""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)


def test_connection() -> dict[str, str]:
    """Test database connection."""
    try:
        engine = create_database_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT NOW();"))
            current_time = result.fetchone()[0]
            return {
                "status": "connected",
                "current_time": str(current_time),
                "database": "local_postgresql",
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
