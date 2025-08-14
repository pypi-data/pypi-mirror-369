import asyncio
import smtplib
from email.message import EmailMessage
from typing import List, Optional

from bmailer.models import EmailPayload


class AsyncMailer:
    def __init__(
        self,
        host: str = "smtp.gmail.com",
        port: int = 587,
        username: str = "",
        password: str = "",
        from_email: Optional[str] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email or username

    def __str__(self) -> str:
        return "AsyncMailer"

    def _send_email_sync(self, subject: str, body: str, recipient: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = recipient
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.username, self.password)
            server.send_message(msg)

    async def send_email(self, subject: str, body: str, recipient: str) -> None:
        await asyncio.to_thread(self._send_email_sync, subject, body, recipient)

    async def _task_sync(self, email: EmailPayload) -> None:
        await self.send_email(email.subject, email.body, email.recipient)

    async def _task_concur(self, email: EmailPayload, sem: asyncio.Semaphore) -> None:
        async with sem:
            await self.send_email(email.subject, email.body, email.recipient)

    async def send_bulk_sync(self, emails: List[EmailPayload]) -> None:
        await asyncio.gather(*[self._task_sync(e) for e in emails])

    async def send_bulk(self, emails: List[EmailPayload], concurrency: int = 5) -> None:
        sem = asyncio.Semaphore(concurrency)
        await asyncio.gather(*[self._task_concur(e, sem) for e in emails])
