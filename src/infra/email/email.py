from dataclasses import dataclass, asdict
from email.message import EmailMessage
from functools import lru_cache
from io import BytesIO
from typing import NamedTuple, Literal, Annotated

from aiosmtplib import send
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import validate_call, ConfigDict, EmailStr

from ...logger import logger
from ...settings import settings


@lru_cache
def _get_template_environment():
    return Environment(
        loader=FileSystemLoader("./templates"),
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
    *recipients: Annotated[str, EmailStr],
    context: EmailContext,
    subject: str | None = None,
    importance: Literal["high", "normal", "low"] = "high",
    attachments: list[Attachment] | None = None,
    **additional_context,
):
    """
    Send an email using a template.

    The `context` parameter is a dataclass that should contain the variables
    that are used in the template. The `subject` parameter is optional and if
    not provided, the value of `context.__subject__` will be used.

    The `importance` parameter is used to set the importance of the email.
    It can be either "high", "normal" or "low".

    The `attachments` parameter is a list of `Attachment` namedtuples.
    The `filename` attribute is the filename of the attachment and the
    `content` attribute is a `BytesIO` object with the content of the file.

    :param recipients: The recipients of the email
    :param context: The context of the email
    :param subject: The subject of the email
    :param importance: The importance of the email
    :param attachments: The attachments of the email
    """
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
    message["To"] = ", ".join(recipients)
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
            recipients=recipients,
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
