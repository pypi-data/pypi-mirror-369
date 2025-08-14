import os
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

from bmailer import AsyncMailer
from bmailer.models import EmailPayload

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

RECIPIENT = os.getenv("RECIPIENT", "")
BODY = "This is a test email."
SUBJECT = "Test Email"

async_mailer = AsyncMailer(
    host=SMTP_HOST,
    port=SMTP_PORT,
    username=SMTP_USERNAME,
    password=SMTP_PASSWORD,
)

email = EmailPayload(subject=SUBJECT, recipient=RECIPIENT, body=BODY)


def test_async_mailer_initialization():
    assert async_mailer is not None
    assert hasattr(async_mailer, "send_email")
    assert hasattr(async_mailer, "send_bulk")
    assert async_mailer.host == SMTP_HOST
    assert async_mailer.port == SMTP_PORT
    assert async_mailer.username == SMTP_USERNAME or SMTP_USERNAME == ""
    assert async_mailer.from_email == SMTP_USERNAME or SMTP_USERNAME == ""
    assert str(async_mailer) == "AsyncMailer"


# @pytest.mark.asyncio
# async def test_async_mailer_integration_concurr():
#     await async_mailer.send_bulk(emails=[email] * 2, concurrency=2)


# @pytest.mark.asyncio
# async def test_async_mailer_integration_sync():
#     await async_mailer.send_bulk_sync(emails=[email])


@pytest.mark.asyncio
async def test_async_mailer_integration_sync():
    async_mailer = AsyncMailer()
    with patch("smtplib.SMTP", autospec=True) as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        await async_mailer.send_bulk_sync([email])
        mock_server.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_async_mailer_integration_concurr():
    async_mailer = AsyncMailer()
    with patch("smtplib.SMTP", autospec=True) as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        await async_mailer.send_bulk([email], concurrency=5)
        mock_server.send_message.assert_called_once()
