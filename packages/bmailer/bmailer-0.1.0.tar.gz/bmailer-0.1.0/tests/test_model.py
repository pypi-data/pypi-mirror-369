from bmailer.models import EmailPayload


def test_model_email_payload() -> None:
    subject = "Test Subject"
    body = "This is a test email body."
    recipient = "email@email.com"
    email_payload = EmailPayload(subject=subject, body=body, recipient=recipient)
    assert email_payload.subject == subject
    assert email_payload.body == body
    assert email_payload.recipient == recipient
