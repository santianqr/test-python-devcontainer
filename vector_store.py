"""Vector store operations for business knowledge."""

import os
from typing import Any

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text

from database import BusinessKnowledge, get_database_url, get_session


class BusinessKnowledgeStore:
    """Manages business knowledge with vector search capabilities."""

    def __init__(self):
        """Initialize the business knowledge store."""
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.database_url = get_database_url()

    def add_knowledge(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add business knowledge to the vector store."""
        session = get_session()
        try:
            embedding = self.embeddings.embed_query(content)

            knowledge = BusinessKnowledge(content=content, embedding=embedding, meta_data=metadata or {})

            session.add(knowledge)
            session.commit()
        finally:
            session.close()

    def search_knowledge(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search for relevant business knowledge."""
        session = get_session()
        try:
            query_embedding = self.embeddings.embed_query(query)

            results = (
                session.query(BusinessKnowledge)
                .order_by(BusinessKnowledge.embedding.cosine_distance(query_embedding))
                .limit(limit)
                .all()
            )

            return [
                {
                    "content": result.content,
                    "metadata": result.meta_data,
                    "similarity": 1.0,  # Placeholder for actual similarity score
                }
                for result in results
            ]
        finally:
            session.close()

    def setup_vector_extension(self) -> bool:
        """Ensure pgvector extension is enabled."""
        session = get_session()
        try:
            session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            session.commit()
            return True
        except Exception as e:
            print(f"Error setting up vector extension: {e}")
            return False
        finally:
            session.close()

    def create_vector_index(self) -> bool:
        """Create vector index for better performance."""
        session = get_session()
        try:
            session.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS business_knowledge_embedding_idx 
                ON business_knowledge USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
                """
                )
            )
            session.commit()
            return True
        except Exception as e:
            print(f"Error creating vector index: {e}")
            return False
        finally:
            session.close()


def init_sample_knowledge():
    """Initialize with sample business knowledge."""
    store = BusinessKnowledgeStore()

    sample_knowledge = [
        {
            "content": (
                "We manage 3 premium Airbnb properties in Miami: Ocean View Apartment in Miami Beach "
                "($150/night), Downtown Miami Loft ($120/night), and Brickell High-Rise Condo ($200/night)."
            ),
            "metadata": {"category": "properties", "location": "miami", "type": "overview"},
        },
        {
            "content": (
                "Ocean View Apartment (miami_beach_01) is a 2BR/2BA with direct ocean views, "
                "accommodates 4 guests, includes pool and gym access."
            ),
            "metadata": {"category": "properties", "property_id": "miami_beach_01", "type": "details"},
        },
        {
            "content": (
                "Downtown Miami Loft (downtown_02) is a modern loft in downtown, accommodates 2 guests, "
                "features city views and rooftop terrace."
            ),
            "metadata": {"category": "properties", "property_id": "downtown_02", "type": "details"},
        },
        {
            "content": (
                "Brickell High-Rise Condo (brickell_03) is a luxury condo with bay views, "
                "accommodates 6 guests, includes spa and concierge services."
            ),
            "metadata": {"category": "properties", "property_id": "brickell_03", "type": "details"},
        },
        {
            "content": (
                "Standard check-in time is 3:00 PM and check-out time is 11:00 AM for most properties. "
                "Brickell condo has 4:00 PM check-in."
            ),
            "metadata": {"category": "policies", "type": "checkin_checkout"},
        },
        {
            "content": (
                "We offer 24/7 customer support for all guests during their stay. "
                "Contact us via WhatsApp for immediate assistance."
            ),
            "metadata": {"category": "support", "availability": "24_7"},
        },
        {
            "content": (
                "Cancellation policy allows free cancellation up to 48 hours before check-in. "
                "Cancellations within 48 hours are subject to one night charge."
            ),
            "metadata": {"category": "policies", "type": "cancellation"},
        },
        {
            "content": (
                "All properties include free WiFi, fully equipped kitchen, parking, and professional cleaning. "
                "Premium properties include additional amenities."
            ),
            "metadata": {"category": "amenities", "type": "standard"},
        },
        {
            "content": (
                "For availability checks, provide property ID (miami_beach_01, downtown_02, or brickell_03) "
                "and desired dates in YYYY-MM-DD format."
            ),
            "metadata": {"category": "booking", "type": "instructions"},
        },
        {
            "content": (
                "Peak season rates apply during December-April. Off-season discounts available May-November. "
                "Weekly stays get 10% discount."
            ),
            "metadata": {"category": "pricing", "type": "seasonal"},
        },
    ]

    for knowledge in sample_knowledge:
        store.add_knowledge(knowledge["content"], knowledge["metadata"])

    print("Sample business knowledge added successfully!")
