# BMailer

[![image](https://img.shields.io/pypi/v/bmailer.svg)](https://pypi.python.org/pypi/bmailer)
[![image](https://img.shields.io/pypi/l/bmailer.svg)](https://pypi.python.org/pypi/bmailer)
[![image](https://img.shields.io/pypi/pyversions/bmailer.svg)](https://pypi.python.org/pypi/bmailer)
[![Actions status](https://github.com/duytanisme/bmailer/actions/workflows/test-and-release.yaml/badge.svg)](https://github.com/duytanisme/bmailer/actions)
[![codecov](https://codecov.io/gh/duytanisme/bmailer/branch/main/graph/badge.svg)](https://codecov.io/gh/duytanisme/bmailer)

BMailer is an asynchronous email sender built with Python, designed to send bulk emails efficiently using SMTP. It supports templating for email bodies and allows for concurrent sending of multiple emails.

## Example Usage

```python
import asyncio

from bmailer import AsyncMailer
from bmailer.models import EmailPayload
from bmailer.templates import render_template


async def main():
    sender = AsyncMailer(
        host="smtp.gmail.com",
        port=587,
        username="email@email.com",
        password="app_password", # If using Gmail, use an App Password
    )

    template = "Hello {name},\nYour order #{order_id} has been shipped."
    emails = [
        EmailPayload(
            subject="Order Update",
            recipient="target@email.com",
            body=render_template(template, name="Recipient", order_id=123),
        ),
    ]

    await sender.send_bulk(emails, concurrency=5)


if __name__ == "__main__":
    asyncio.run(main())
```

## Installation

```bash
pip install bmailer
```

## Contribution

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

```bash
git clone https://github.com/duytanisme/bmailer.git
cd bmailer
uv sync
```
