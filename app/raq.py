"""
RAG (Retrieval-Augmented Generation) System.
Uses FAISS for efficient semantic search over documents.
"""

import logging
import numpy as np
import pandas as pd
from typing import List
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Retrieval-Augmented Generation system using FAISS.
    
    Stores documents and uses semantic search to retrieve
    relevant context for question answering.
    """
    
    def __init__(self, path: str):
        """
        Initialize RAG system with documents.
        
        Args:
            path: Path to parquet file with columns 'instruction' and 'output'
        """
        try:
            logger.info(f"Loading RAG data from {path}")
            
            # Load embedder model
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Load documents
            df = pd.read_parquet(path)
            self.questions = df["instruction"].tolist()
            self.answers = df["output"].tolist()
            
            logger.info(f"Loaded {len(self.questions)} documents")
            
            # Create embeddings
            logger.info("Creating embeddings...")
            self.emb = self.model.encode(self.questions)
            
            # Create FAISS index
            self.index = faiss.IndexFlatL2(self.emb.shape[1])
            self.index.add(np.array(self.emb, dtype=np.float32))
            
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise

    def query(self, text: str, k: int = 3) -> List[str]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            text: Query text
            k: Number of documents to retrieve (default 3)
            
        Returns:
            List of relevant document texts
        """
        try:
            # Encode query
            q = self.model.encode([text])
            
            # Search FAISS index
            D, I = self.index.search(np.array(q, dtype=np.float32), k)
            
            # Get corresponding answers
            results = [self.answers[i] for i in I[0]]
            
            logger.debug(f"RAG query returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return []
