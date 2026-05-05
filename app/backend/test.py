from services.rag_service import RAGService

rag_service = RAGService()


query = "Tôi nên học ngành AI"
docs = rag_service.retrieve(query, user_id="test")

print(docs)