-- Initialize PostgreSQL database for WhatsApp AI Assistant
-- This script runs automatically when PostgreSQL starts

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the database if it doesn't exist (this runs in postgres DB context)
-- The main database is already created by POSTGRES_DB env var

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE whatsapp_ai TO postgres;

-- Connect to the whatsapp_ai database for table creation
\c whatsapp_ai;

-- Enable pgvector extension in the target database too
CREATE EXTENSION IF NOT EXISTS vector;

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    chat_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on chat_id for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_chat_id ON conversations(chat_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);

-- Create business_knowledge table with vector column
CREATE TABLE IF NOT EXISTS business_knowledge (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    meta_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index for similarity search
-- Note: We'll create this index later when we have some data
-- CREATE INDEX business_knowledge_embedding_idx ON business_knowledge 
-- USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create index on created_at for better performance
CREATE INDEX IF NOT EXISTS idx_business_knowledge_created_at ON business_knowledge(created_at);

-- Insert some sample business knowledge
INSERT INTO business_knowledge (content, meta_data) VALUES 
(
    'Somos una empresa de gestión de propiedades de Airbnb. Ofrecemos servicios completos de administración, limpieza, mantenimiento y atención al huésped las 24 horas.',
    '{"type": "company_info", "category": "general"}'
),
(
    'Nuestros precios varían según la temporada. Temporada alta: diciembre-febrero y julio-agosto. Temporada media: marzo-junio y septiembre-noviembre. Temporada baja: resto del año.',
    '{"type": "pricing", "category": "seasonal"}'
),
(
    'Para reservas, los huéspedes deben hacer check-in después de las 15:00 y check-out antes de las 11:00. Ofrecemos check-in automático con códigos de acceso.',
    '{"type": "policy", "category": "checkin"}'
),
(
    'Aceptamos mascotas en propiedades seleccionadas con un cargo adicional de $25 por noche. Las mascotas deben estar registradas antes de la llegada.',
    '{"type": "policy", "category": "pets"}'
),
(
    'Política de cancelación: Cancelación gratuita hasta 48 horas antes del check-in. Después de eso, se cobra el 50% del total. No hay reembolso el día del check-in.',
    '{"type": "policy", "category": "cancellation"}'
);

-- Grant permissions to ensure the application can access everything
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Print completion message
SELECT 'Database initialization completed successfully!' as status;
