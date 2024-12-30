from langflow.load import run_flow_from_json
TWEAKS = {
  "ChatInput-b0cUC": {},
  "Prompt-QSQkL": {},
  "ChatOutput-LkvHf": {},
  "OpenAIEmbeddings-9pSYz": {},
  "RetrieverTool-IVprE": {},
  "Agent-MKssF": {},
  "SerpAPI-CpoxH": {},
  "SupabaseVectorStore-4ruHX": {}
}

result = run_flow_from_json(flow="rag.json",
                            input_value="message",
                            session_id="", # provide a session id if you want to use session state
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)