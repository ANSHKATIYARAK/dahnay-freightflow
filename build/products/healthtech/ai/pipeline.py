from pydantic import BaseModel, Field
from typing import List

class HealthTechClinicOpsInferenceOutput(BaseModel):
    domain: str = 'HealthTech / ClinicOps'
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detected_anomalies: List[str]
    recommended_action: str

# RAG Chunking & Embeddings Query
def build_rag_prompt(query: str, retrieved_chunks: list) -> str:
    context = '\n'.join(retrieved_chunks)
    return f'Domain: HealthTech / ClinicOps\nContext: {context}\nQuery: {query}'
