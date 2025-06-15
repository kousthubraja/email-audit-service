from django.contrib import admin
from .models import RuleOutcome, AuditReport

@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = ('thread', 'overall_score', 'created_at', 'completed_at')
    search_fields = ('thread__subject', 'generated_by__name')
    list_filter = ('created_at', 'completed_at')
    readonly_fields = ('overall_score', 'strengths', 'improvements')


@admin.register(RuleOutcome)
class RuleOutcomeAdmin(admin.ModelAdmin):
    list_display = ('report', 'rule', 'passed', 'score', 'email_message', )
    search_fields = ('report__thread__subject', 'rule__name', 'email_message__subject')
    list_filter = ('passed', 'report__created_at')
    readonly_fields = ('justification',)
    
    def has_add_permission(self, request, obj=None):
        return False