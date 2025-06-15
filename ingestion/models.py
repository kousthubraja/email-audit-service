from django.db import models


class EmailThread(models.Model):
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread: {self.subject} (ID: {self.id})"


class EmailMessage(models.Model):
    thread = models.ForeignKey(
        EmailThread,
        related_name="messages",
        on_delete=models.CASCADE
    )
    message_id = models.CharField(max_length=255, unique=True)
    sender = models.EmailField()
    recipients = models.JSONField(help_text="List of recipient email addresses")
    cc = models.JSONField(blank=True, null=True, help_text="List of CC email addresses")
    bcc = models.JSONField(blank=True, null=True, help_text="List of BCC email addresses")
    date = models.DateTimeField()
    subject = models.CharField(max_length=255)
    body_text = models.TextField(blank=True)
    body_html = models.TextField(blank=True)
    raw_content = models.TextField(help_text="Raw .eml content")
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmailMessage: {self.message_id} from {self.sender}"
