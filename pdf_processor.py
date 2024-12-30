import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase.client import create_client

# Load environment variables
load_dotenv()

class PDFProcessor:
    def __init__(self, pdf_directory: str):
        self.pdf_directory = pdf_directory
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize Supabase client
        self.supabase_client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key
        )

    def load_documents(self) -> List:
        """Load PDF documents from the specified directory"""
        loader = DirectoryLoader(
            self.pdf_directory,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
        return documents

    def split_documents(self, documents: List, chunk_size: int = 1000) -> List:
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False
        )
        splits = text_splitter.split_documents(documents)
        return splits

    def create_embeddings_and_store(self, document_chunks: List) -> None:
        """Create embeddings and store in Supabase"""
        vector_store = SupabaseVectorStore.from_documents(
            documents=document_chunks,
            embedding=self.embeddings,
            client=self.supabase_client,
            table_name="documents",  # Update with your table name
            query_name="match_documents"  # Update with your query name
        )
        return vector_store

    def process_pdfs(self) -> None:
        """Main method to process PDFs and store in Supabase"""
        try:
            print(f"Loading documents from {self.pdf_directory}")
            documents = self.load_documents()
            print(f"Loaded {len(documents)} documents")

            print("Splitting documents into chunks")
            document_chunks = self.split_documents(documents)
            print(f"Created {len(document_chunks)} document chunks")

            print("Creating embeddings and storing in Supabase")
            vector_store = self.create_embeddings_and_store(document_chunks)
            print("Successfully stored embeddings in Supabase")

        except Exception as e:
            print(f"Error processing PDFs: {str(e)}")
            raise

def main():
    # Create a .env file with your API keys and credentials
    """
    SUPABASE_URL=your_supabase_url
    SUPABASE_SERVICE_KEY=your_supabase_key
    OPENAI_API_KEY=your_openai_api_key
    """
    
    # Specify your PDF directory
    pdf_directory = "path/to/your/pdfs"
    
    # Initialize and run the processor
    processor = PDFProcessor(pdf_directory)
    processor.process_pdfs()

if __name__ == "__main__":
    main()