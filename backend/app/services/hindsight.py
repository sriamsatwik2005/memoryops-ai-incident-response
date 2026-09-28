from hindsight_client import Hindsight
from app.core.config import settings

class HindsightService:
    def __init__(self):
        kwargs = {"base_url": settings.hindsight_base_url}
        if settings.hindsight_api_key:
            kwargs["api_key"] = settings.hindsight_api_key
        self.client = Hindsight(**kwargs)
        self.bank_id = settings.hindsight_bank_id

    def recall_incidents(self, query: str):
        result = self.client.recall(
            bank_id=self.bank_id,
            query=query,
            types=["experience", "observation"],
            max_tokens=4096,
            budget="mid",
        )
        return [
            {"id": getattr(r, "id", None), "text": r.text, "type": r.type, "context": getattr(r, "context", None)}
            for r in result.results
        ]

    def retain_incident(self, content: str, incident_id: str):
        return self.client.retain(
            bank_id=self.bank_id,
            content=content,
            context="Production incident response experience",
            document_id=incident_id,
            metadata={"source": "memoryops", "incident_id": incident_id},
        )
