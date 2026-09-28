import json

from openai import OpenAI

from app.core.config import settings
from app.services.hindsight import HindsightService


class IncidentAgent:
    def __init__(self):
        self.memory = HindsightService()

        self.llm = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    def investigate(self, incident: dict):
        # ---------------------------------------------------------
        # 1. Build a query for Hindsight
        # ---------------------------------------------------------
        query = (
            "Find previous production incidents that are similar to this incident. "
            f"Service={incident.get('service', '')}; "
            f"Summary={incident.get('summary', '')}; "
            f"Logs={incident.get('logs', '')}; "
            f"Metrics={incident.get('metrics', '')}; "
            f"Deployment={incident.get('deployment', '')}"
        )

        # ---------------------------------------------------------
        # 2. Recall historical incidents from Hindsight
        # ---------------------------------------------------------
        memories = self.memory.recall_incidents(query)

        memory_text = "\n\n".join(
            f"Memory {i + 1}: {memory.get('text', '')}"
            for i, memory in enumerate(memories[:5])
        )

        if not memory_text:
            memory_text = "No relevant historical memories found."

        # ---------------------------------------------------------
        # 3. Ask the LLM to analyze the incident
        # ---------------------------------------------------------
        prompt = f"""
You are an SRE incident-response agent.

Analyze the current production incident using:
1. Current incident evidence
2. Historical incidents retrieved from Hindsight

Use historical incidents as supporting evidence, but do not blindly copy
their conclusions.

Do not claim certainty when the evidence is insufficient.

Return ONLY valid JSON.

The JSON MUST contain exactly these keys:

{{
    "root_cause": "short explanation of the likely root cause",
    "confidence": 0.0,
    "recommendation": [
        "recommended action 1",
        "recommended action 2"
    ],
    "reasoning": "explanation of how the evidence and historical memories support the analysis"
}}

IMPORTANT:
- confidence MUST normally be a number between 0 and 1.
- recommendation MUST be a JSON array of strings.
- Do not use Markdown.
- Do not wrap the JSON in ```json.
- Do not add any text before or after the JSON.

CURRENT INCIDENT:
{json.dumps(incident, indent=2)}

HISTORICAL HINDSIGHT MEMORIES:
{memory_text}
"""

        # ---------------------------------------------------------
        # 4. Call the LLM
        # ---------------------------------------------------------
        response = self.llm.chat.completions.create(
            model=settings.llm_model,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful production SRE assistant. "
                        "Return structured JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        # ---------------------------------------------------------
        # 5. Extract LLM response
        # ---------------------------------------------------------
        content = response.choices[0].message.content or "{}"

        content = content.strip()

        # Remove Markdown code fences if the model still adds them
        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # ---------------------------------------------------------
        # 6. Parse JSON
        # ---------------------------------------------------------
        try:
            analysis = json.loads(content)

        except json.JSONDecodeError:
            # Attempt to extract the JSON object if the model
            # accidentally added extra text around it.
            start = content.find("{")
            end = content.rfind("}")

            if start != -1 and end != -1 and end > start:
                try:
                    analysis = json.loads(content[start:end + 1])
                except json.JSONDecodeError:
                    raise ValueError(
                        f"LLM returned invalid JSON:\n{content}"
                    )
            else:
                raise ValueError(
                    f"LLM returned invalid JSON:\n{content}"
                )

        # ---------------------------------------------------------
        # 7. Normalize root cause
        # ---------------------------------------------------------
        root_cause = analysis.get("root_cause")

        if root_cause is None:
            root_cause = "Unable to determine root cause from available evidence."

        elif not isinstance(root_cause, str):
            root_cause = str(root_cause)

        analysis["root_cause"] = root_cause

        # ---------------------------------------------------------
        # 8. Normalize confidence
        # ---------------------------------------------------------
        confidence = analysis.get("confidence")

        if isinstance(confidence, str):

            confidence_text = confidence.lower().strip()

            confidence_map = {
                "very low": 0.2,
                "low": 0.4,
                "medium": 0.6,
                "high": 0.9,
                "very high": 0.95,
            }

            # Handle strings such as "90%" or "0.9"
            try:
                if confidence_text.endswith("%"):
                    confidence = float(
                        confidence_text.replace("%", "").strip()
                    ) / 100

                else:
                    confidence = float(confidence_text)

            except ValueError:
                confidence = confidence_map.get(
                    confidence_text,
                    0.5,
                )

        elif isinstance(confidence, (int, float)):
            confidence = float(confidence)

        else:
            confidence = 0.5

        # Keep confidence safely between 0 and 1
        confidence = max(0.0, min(1.0, confidence))

        analysis["confidence"] = confidence

        # ---------------------------------------------------------
        # 9. Normalize recommendation
        # ---------------------------------------------------------
        recommendation = analysis.get("recommendation")

        if recommendation is None:
            recommendation = [
                "Collect additional evidence before taking remediation action."
            ]

        elif isinstance(recommendation, str):
            recommendation = [recommendation]

        elif isinstance(recommendation, list):
            recommendation = [
                str(item)
                for item in recommendation
                if item is not None
            ]

        else:
            recommendation = [str(recommendation)]

        if not recommendation:
            recommendation = [
                "Collect additional evidence before taking remediation action."
            ]

        analysis["recommendation"] = recommendation

        # ---------------------------------------------------------
        # 10. Normalize reasoning
        # ---------------------------------------------------------
        reasoning = analysis.get("reasoning")

        if reasoning is None:
            reasoning = "The available evidence was insufficient for detailed reasoning."

        elif not isinstance(reasoning, str):
            reasoning = str(reasoning)

        analysis["reasoning"] = reasoning

        # ---------------------------------------------------------
        # 11. Add incident ID
        # ---------------------------------------------------------
        analysis["incident_id"] = incident["external_id"]

        # ---------------------------------------------------------
        # 12. Attach Hindsight memories
        # ---------------------------------------------------------
        analysis["memories"] = memories[:5]

        return analysis

    def retain_resolution(self, incident: dict):
        # ---------------------------------------------------------
        # Build a structured memory from the resolved incident
        # ---------------------------------------------------------
        content = f"""
Incident ID: {incident.get('external_id')}
Service: {incident.get('service')}
Summary: {incident.get('summary')}
Severity: {incident.get('severity')}

Logs:
{incident.get('logs')}

Metrics:
{incident.get('metrics')}

Deployment:
{incident.get('deployment')}

Root Cause:
{incident.get('root_cause')}

Resolution:
{incident.get('resolution')}

Outcome:
Successfully resolved after incident investigation and remediation.

This incident should be used as historical production experience
when investigating future incidents involving the same service,
symptoms, metrics, logs, or deployment patterns.
""".strip()

        # ---------------------------------------------------------
        # Store the resolved incident in Hindsight
        # ---------------------------------------------------------
        return self.memory.retain_incident(
            content,
            incident["external_id"],
        )