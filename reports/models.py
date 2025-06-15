from django.db import models
from ingestion.models import EmailThread, EmailMessage
from rules.models import Rule
from users.models import Contact


class AuditReport(models.Model):
    thread = models.ForeignKey(
        EmailThread,
        related_name="audit_reports",
        on_delete=models.CASCADE
    )
    generated_by = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_reports"
    )
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Aggregated compliance score"
    )
    strengths = models.TextField(help_text="Summary of passed rules and best practices")
    improvements = models.TextField(help_text="Summary of failed rules and suggestions")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AuditReport for Thread {self.thread.id} @ {self.created_at.date()}"


class RuleOutcome(models.Model):
    report = models.ForeignKey(
        AuditReport,
        related_name="rule_outcomes",
        on_delete=models.CASCADE
    )
    rule = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE
    )
    email_message = models.ForeignKey(
        EmailMessage,
        on_delete=models.CASCADE
    )
    passed = models.BooleanField()
    score = models.IntegerField(help_text="Points awarded for this rule evaluation")
    justification = models.TextField()

    class Meta:
        unique_together = ("report", "rule", "email_message")

    def __str__(self):
        status = "Pass" if self.passed else "Fail"
        return f"{self.rule.name} on Message {self.email_message.id}: {status}"
