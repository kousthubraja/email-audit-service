import os
from celery import shared_task
from audit.tasks import audit_email
from ingestion.models import EmailThread, EmailMessage
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import email


@shared_task(bind=True)
def process_eml_file(self, eml_path):
    """
    Celery task to parse a .eml file, create EmailThread and EmailMessage records.
    Handles both single messages and multipart/digest containing multiple messages.
    """
    if not os.path.exists(eml_path):
        raise FileNotFoundError(f"EML file not found: {eml_path}")

    # Parse .eml file
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    messages_processed = 0
    thread = None

    # Check if this is a multipart/digest (contains multiple embedded messages)
    if msg.get_content_type() == 'multipart/digest':
        # Process each embedded message
        for part in msg.iter_parts():
            if part.get_content_type() == 'message/rfc822':
                # Extract the embedded message
                embedded_msg = part.get_payload()[0]
                thread, created = process_single_message(embedded_msg, thread)
                messages_processed += 1
    else:
        # Process as a single message
        thread, created = process_single_message(msg, thread)
        messages_processed += 1

    # Trigger the audit task if this is a new thread or if we processed multiple messages
    if thread and (messages_processed > 1 or thread.messages.count() == 1):
        audit_email.delay(thread.id)

    return {
        'thread_id': thread.id if thread else None, 
        'messages_processed': messages_processed,
        'total_messages_in_thread': thread.messages.count() if thread else 0
    }


def process_single_message(msg, existing_thread=None):
    """
    Process a single email message and create EmailMessage record.
    Returns (thread, created) tuple.
    """
    # Extract basic fields
    subject = msg.get('subject', '(no subject)')
    message_id = msg.get('message-id')
    
    # Create or get thread
    if existing_thread:
        thread = existing_thread
        created = False
    else:
        # Try to find existing thread by subject or create new one
        thread, created = EmailThread.objects.get_or_create(subject=subject)

    # Extract recipients, cc, bcc
    to_addrs = msg.get_all('to', [])
    cc_addrs = msg.get_all('cc', [])
    bcc_addrs = msg.get_all('bcc', [])

    # Parse the date field properly
    date_str = msg.get('date')
    parsed_date = None
    if date_str:
        try:
            parsed_date = parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            parsed_date = None

    # Extract body content
    body_text = ''
    body_html = ''
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body_text = part.get_content()
                break
            elif part.get_content_type() == 'text/html' and not body_html:
                body_html = part.get_content()
    else:
        if msg.get_content_type() == 'text/plain':
            body_text = msg.get_content()
        elif msg.get_content_type() == 'text/html':
            body_html = msg.get_content()

    # Create message record (check if it already exists to avoid duplicates)
    email_message, msg_created = EmailMessage.objects.get_or_create(
        message_id=message_id,
        defaults={
            'thread': thread,
            'sender': msg.get('from'),
            'recipients': to_addrs or [],
            'cc': cc_addrs or [],
            'bcc': bcc_addrs or [],
            'date': parsed_date,
            'subject': subject,
            'body_text': body_text,
            'body_html': body_html,
            'raw_content': msg.as_string()
        }
    )

    return thread, created
