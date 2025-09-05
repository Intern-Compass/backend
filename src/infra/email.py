from dataclasses import dataclass, asdict
from email.message import EmailMessage
from functools import lru_cache

from aiosmtplib import send
from jinja2 import Environment, FileSystemLoader, select_autoescape

from io import BytesIO
from typing import NamedTuple, Literal

from pydantic import validate_call, ConfigDict

from src.logger import logger
from src.settings import settings


@lru_cache
def _get_template_environment():
    return Environment(
        loader=FileSystemLoader(settings.TEMPLATES_FOLDER),
        autoescape=select_autoescape(["html", "xml"]),
    )


class Attachment(NamedTuple):
    filename: str
    content: BytesIO


@dataclass(kw_only=True)
class EmailContext:
    __template_path__: str
    __subject__: str

    def to_dict(self):
        data = asdict(
            self,
            dict_factory=lambda x: {k: v for k, v in x if not k.startswith("_")},
        )
        return data


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
async def send_email(
    context: EmailContext,
    subject: str | None = None,
    importance: Literal["high", "normal", "low"] = "high",
    attachments: list[Attachment] | None = None,
    **additional_context,
):
    # Set the subject and render the template
    subject = subject or context.__subject__
    markup = (
        _get_template_environment()
        .get_template(context.__template_path__)
        .render(**context.to_dict(), **additional_context)
    )

    # Create a message
    message = EmailMessage()
    message["From"] = (
        f"{settings.SMTP_SENDER_NAME} <{settings.SMTP_SENDER_EMAIL}>"
        if settings.SMTP_SENDER_NAME
        else settings.SMTP_SENDER_EMAIL
    )
    message["To"] = ", ".join(settings.SMTP_RECEPIENTS)
    message["Subject"] = subject
    message.set_content(markup, subtype="html")
    message["Importance"] = importance

    # Add attachments
    if attachments:
        for attachment in attachments:
            message.add_attachment(
                attachment.content.getvalue(),
                filename=attachment.filename,
                maintype="application",
                subtype="octet-stream",
            )

    # Send the message
    try:
        await send(
            message,
            sender=settings.SMTP_USERNAME,
            recipients=settings.SMTP_RECEPIENTS,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_PORT == 465,
            start_tls=settings.SMTP_PORT == 587,
        )
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
