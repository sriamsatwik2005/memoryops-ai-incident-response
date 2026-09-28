from app.db.session import Base, engine, SessionLocal
from app.models.incident import Incident

Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(Incident).count():
    incidents = [
        Incident(
            external_id="INC-0782", service="payment-api", severity="HIGH", status="RESOLVED",
            summary="Payment API latency increased after deployment",
            logs="Redis connection pool exhausted; max connections reached",
            metrics="latency=3.4s; error_rate=17%; redis_connections=498/500",
            deployment="v2.3.8", root_cause="Redis connection pool configuration",
            resolution="Increased pool size from 50 to 150"
        ),
        Incident(
            external_id="INC-1042", service="payment-api", severity="HIGH", status="RESOLVED",
            summary="Payment API returned elevated 500 errors",
            logs="Redis connection acquisition timeout",
            metrics="latency=3.2s; error_rate=18%; redis_connections=499/500",
            deployment="v2.4.1", root_cause="Redis connection pool exhaustion",
            resolution="Increased connection pool and restarted affected pods"
        ),
        Incident(
            external_id="INC-1108", service="auth-service", severity="CRITICAL", status="OPEN",
            summary="Authentication requests timing out",
            logs="Database connection timeout after 30 seconds",
            metrics="latency=8.1s; error_rate=31%; db_connections=100/100",
            deployment="v1.9.2"
        ),
    ]
    db.add_all(incidents)
    db.commit()
print("Seed complete")
