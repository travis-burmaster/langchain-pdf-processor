# LangChain PDF Processor

A Python application that processes PDFs using LangChain and stores document embeddings in a Supabase vector database. This tool is perfect for creating searchable document repositories with semantic search capabilities.

## Features

- Recursive PDF loading from directories
- Smart document splitting with configurable chunk sizes
- OpenAI embeddings generation
- Supabase vector database integration
- Error handling and logging
- Clean, class-based architecture

## Prerequisites

Before you begin, ensure you have:

1. Python 3.7+ installed
2. A Supabase account and project
3. An OpenAI API key
4. Your PDF documents ready for processing

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
create or replace function match_documents_bulk(query_embedding vector(1536), match_count int)
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
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
```

2. Update the following in `pdf_processor.py`:
- `query_name`: Your similarity search function name (default is 'match_documents_bulk')
- `pdf_directory`: Path to your PDF files

## Usage

1. Place your PDF files in a directory

2. Update the `pdf_directory` in the main function:
```python
ENV.pdf_directory = "path/to/your/pdfs"
```

3. Run the processor:
```bash
python pdf_processor.py
```

## How It Works

1. The application recursively scans the specified directory for PDF files
2. Each PDF is loaded and split into manageable chunks
3. OpenAI's API generates embeddings for each chunk
4. The embeddings are stored in your Supabase vector database
5. You can then use these embeddings for semantic search and document retrieval

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.