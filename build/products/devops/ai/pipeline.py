from pydantic import BaseModel, Field
from typing import List

class DevOpsCloudInfraInferenceOutput(BaseModel):
    domain: str = 'DevOps / Cloud Infra'
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detected_anomalies: List[str]
    recommended_action: str

# RAG Chunking & Embeddings Query
def build_rag_prompt(query: str, retrieved_chunks: list) -> str:
    context = '\n'.join(retrieved_chunks)
    return f'Domain: DevOps / Cloud Infra\nContext: {context}\nQuery: {query}'
