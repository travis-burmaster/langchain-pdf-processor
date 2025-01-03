import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from dotenv import load_dotenv
import json
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
from langflow import load_flow_from_json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize clients and models
def init_clients():
    try:
        # Load Langflow configuration
        with open('rag.json', 'r') as f:
            flow_config = json.load(f)
        
        # Initialize Supabase client for vector store
        supabase_client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize Supabase vector store
        vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=embeddings,
            table_name="bulk_documents",
            query_name="match_documents_bulk"
        )
        
        # Initialize Langflow chain
        flow = load_flow_from_json(flow_config)
        # Update the retriever in the flow with our vector store
        for node in flow['nodes']:
            if node.get('type') == 'RetrieverTool':
                node['data']['retriever'] = vector_store.as_retriever(search_kwargs={'k': 3})
        
        chain = flow.get_chain()
        return chain
    
    except Exception as e:
        print(f"Error initializing clients: {str(e)}")
        raise

# Initialize the chain
try:
    rag_chain = init_clients()
except Exception as e:
    print(f"Failed to initialize RAG chain: {str(e)}")
    rag_chain = None

@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/chat')
def chat():
    print('Request for chat page received')
    return render_template('chat.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        if rag_chain is None:
            return jsonify({"error": "RAG chain not initialized"}), 500

        data = request.json
        query_text = data.get('query')
        chat_history = data.get('chat_history', [])

        if not query_text:
            return jsonify({"error": "No query provided"}), 400

        print(f'Processing chat query: {query_text}')

        # Convert chat history to the format expected by the chain
        formatted_history = [(msg["human"], msg["ai"]) for msg in chat_history]

        # Get response from the chain
        response = rag_chain.invoke({
            "question": query_text, 
            "chat_history": formatted_history
        })

        # Extract source documents if available
        sources = []
        if hasattr(response, 'source_documents'):
            sources = [{
                "content": doc.page_content,
                "metadata": doc.metadata
            } for doc in response.source_documents]
        else:
            # Handle different response formats from Langflow
            response_dict = response if isinstance(response, dict) else response.dict()
            sources = response_dict.get('source_documents', [])

        return jsonify({
            "answer": response.get('answer', str(response)),
            "sources": sources
        })

    except Exception as e:
        print(f'Error processing query: {str(e)}')
        return jsonify({"error": "An error occurred processing your request"}), 500

# Health check endpoint for Azure
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "rag_chain_initialized": rag_chain is not None
    }), 200

if __name__ == '__main__':
    app.run(debug=False)  # Set to True for development