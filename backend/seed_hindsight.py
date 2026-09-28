from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.incident import Incident
from app.agent.incident_agent import IncidentAgent


def main():
    db = SessionLocal()
    agent = IncidentAgent()

    try:
        incidents = db.execute(
            select(Incident).where(Incident.status == "RESOLVED")
        ).scalars().all()

        print(f"Found {len(incidents)} resolved incidents.")

        for incident in incidents:
            data = {
                "external_id": incident.external_id,
                "service": incident.service,
                "summary": incident.summary,
                "logs": incident.logs,
                "metrics": incident.metrics,
                "deployment": incident.deployment,
                "root_cause": incident.root_cause,
                "resolution": incident.resolution,
            }

            print(f"Retaining {incident.external_id}...")
            agent.retain_resolution(data)
            print(f"✓ Retained {incident.external_id}")

        print("\nHindsight seeding complete.")

    finally:
        db.close()


if __name__ == "__main__":
    main()