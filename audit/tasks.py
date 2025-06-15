from celery import shared_task
from ingestion.models import EmailThread
from rules.models import Rule
from reports.models import AuditReport, RuleOutcome
from google import genai
from google.genai import types
from decouple import config

GEMINI_API_KEY = config("GEMINI_API_KEY")
GEMINI_MODEL = config("GEMINI_MODEL", default="gemini-2.5-flash-preview-04-17")

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

@shared_task(bind=True)
def audit_email(self, thread_id):
    """
    Celery task to audit an email thread using dynamic rules and Gemini API.
    """
    thread = EmailThread.objects.get(id=thread_id)
    messages = thread.messages.all()
    rules = Rule.objects.filter(is_active=True)

    report = AuditReport.objects.create(
        thread=thread,
        generated_by=None,
        overall_score=0,
        strengths="",
        improvements=""
    )

    total_score = 0
    outcomes = []

    # Pre-build the response schema
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        required=["passed", "score", "justification"],
        properties={
            "passed": types.Schema(type=types.Type.BOOLEAN),
            "score": types.Schema(type=types.Type.INTEGER),
            "justification": types.Schema(type=types.Type.STRING),
        },
    )

    for msg in messages:
        content_text = msg.body_text or msg.body_html or ""

        for rule in rules:
            # Construct the user prompt
            user_prompt = (
                f"Rule: {rule.name}\n"
                f"Definition: {rule.description}\n"
                f"Email Content:\n{content_text}\n\n"
                "Evaluate this email against the rule and return JSON with keys "
                "'passed' (bool), 'score' (int 0-100), and 'justification' (str)."
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_prompt)],
                )
            ]

            generate_config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                system_instruction=[
                    types.Part.from_text(
                        text="You are an email auditing assistant. Respond strictly in the requested JSON schema."
                    )
                ],
            )

            # Call Gemini
            result = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=generate_config,
            )
            parsed = result.parsed or {}

            passed = parsed.get("passed", False)
            score = parsed.get("score", 0)
            justification = parsed.get("justification", "")

            print(content_text)
            print(f"Rule: {rule.name}, Passed: {passed}, Score: {score}, Justification: {justification}")

            total_score += score
            outcomes.append(RuleOutcome(
                report=report,
                rule=rule,
                email_message=msg,
                passed=passed,
                score=score,
                justification=justification
            ))

    # Bulk create outcomes
    RuleOutcome.objects.bulk_create(outcomes)

    # Compute overall score
    rule_count = rules.count()
    message_count = messages.count()
    denom = message_count * rule_count if rule_count and message_count else 1
    report.overall_score = total_score / denom

    # Summarize strengths and improvements
    passed_rules = [
        r.name for r in rules
        if RuleOutcome.objects.filter(report=report, rule=r, passed=True).exists()
    ]
    failed_rules = [
        r.name for r in rules
        if RuleOutcome.objects.filter(report=report, rule=r, passed=False).exists()
    ]

    report.strengths = "Rules passed: " + ", ".join(passed_rules)
    report.improvements = "Rules failed: " + ", ".join(failed_rules)
    report.save()

    return {"report_id": report.id}