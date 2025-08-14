from dataclasses import dataclass


@dataclass
class EmailPayload:
    body: str
    recipient: str
    subject: str
