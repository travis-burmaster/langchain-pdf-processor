# LangChain PDF Processor with RAG Chat Interface

A Python application that processes PDFs using LangChain and provides a chat interface for querying the documents using RAG (Retrieval Augmented Generation).

## Features

- Recursive PDF loading from directories
- Smart document splitting with configurable chunk sizes
- OpenAI embeddings generation
- Supabase vector database integration
- Web-based chat interface
- RAG-powered document question answering
- Clean, class-based architecture

## Prerequisites

Before you begin, ensure you have:

1. Python 3.7+ installed
2. A Supabase account and project
3. An OpenAI API key
4. Your PDF documents ready for processing
5. A Langflow RAG configuration (rag.json)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/travis-burmaster/langchain-pdf-processor.git
cd langchain-pdf-processor
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Supabase Setup

1. Create a new Supabase project at https://supabase.com

2. Enable Vector support in your database

3. Create a table for documents with vector support:
```sql
create extension if not exists vector;
create extension if not exists "uuid-ossp";

create table bulk_documents (
    id uuid primary key default uuid_generate_v4(),
    content text,
    metadata jsonb,
    embedding vector(1536)
);

create index on bulk_documents using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);
```

4. Create a similarity search function:
```sql
create or replace function match_documents(query_embedding vector(1536), match_count int)
returns table (id uuid, content text, metadata jsonb, similarity float)
language plpgsql
as $$
begin
    return query
    select
        id,
        content,
        metadata,
        1 - (embedding <=> query_embedding) as similarity
    from bulk_documents
    order by embedding <=> query_embedding
    limit match_count;
end;
$$;
```

## Configuration

1. Create a `.env` file in the project root:
```
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional Langflow Configuration
LANGFLOW_API_KEY=your_langflow_api_key  # if required
LANGFLOW_API_HOST=http://localhost:3000  # adjust if different
```

2. Place your Langflow RAG configuration file:
- Export your RAG flow from Langflow as JSON
- Save it as `rag.json` in the project root

## Usage

### 1. Process PDFs

First, process your PDFs to store them in the vector database:

```bash
python pdf_processor.py --directory /path/to/your/pdfs
```

### 2. Run the Chat Interface

Start the Flask web application:

```bash
python app.py
```

The chat interface will be available at `http://localhost:5000`

## Architecture

### PDF Processing Flow
1. Load PDFs recursively from specified directory
2. Split documents into manageable chunks
3. Generate embeddings using OpenAI
4. Store in Supabase vector database

### RAG Chat Flow
1. User sends query through web interface
2. System retrieves relevant document chunks using vector similarity
3. Retrieved context is combined with the query
4. LLM generates response using the context
5. Response and sources are displayed to user

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
