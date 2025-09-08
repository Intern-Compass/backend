from dataclasses import dataclass
from .email import EmailContext


@dataclass(kw_only=True)
class VerifyEmailContext(EmailContext):
    __template_path__: str = "verify_email.html"
    __subject__: str = "Confirm your email address"

    send_code: str


@dataclass(kw_only=True)
class EmailVerifiedContext(EmailContext):
    __template_path__: str = "email_verified.html"
    __subject__: str = "Your email address has been verified"
