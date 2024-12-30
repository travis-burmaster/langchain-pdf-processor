from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import json
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from supabase import create_client

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Supabase and OpenAI clients
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase_client = create_client(supabase_url, supabase_key)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize Supabase vector store
vector_store = SupabaseVectorStore(
    client=supabase_client,
    embedding=embeddings,
    table_name="bulk_documents",
    query_name="match_documents"
)

# Load Langflow configuration
def load_langflow_config():
    config_path = os.path.join(os.path.dirname(__file__), 'rag.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

# Initialize ChatOpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-4-turbo-preview",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize the RAG chain
chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={'k': 3}),
    return_source_documents=True,
    verbose=True
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        query_text = data.get('query')
        chat_history = data.get('chat_history', [])

        # Convert chat history to the format expected by the chain
        formatted_history = [(msg["human"], msg["ai"]) for msg in chat_history]

        # Get response from the chain
        response = chain({
            "question": query_text, 
            "chat_history": formatted_history
        })

        # Extract source documents
        sources = [{
            "content": doc.page_content,
            "metadata": doc.metadata
        } for doc in response["source_documents"]]

        return jsonify({
            "answer": response["answer"],
            "sources": sources
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)  # Set debug=False for production
