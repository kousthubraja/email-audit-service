from django.db import models


class Rule(models.Model):
    SEVERITY_CHOICES = [
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    severity = models.PositiveSmallIntegerField(choices=SEVERITY_CHOICES)
    definition = models.JSONField(help_text="Rule logic definition (JSON/DSL)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
