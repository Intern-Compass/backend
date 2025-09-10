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


@dataclass(kw_only=True)
class UpdatedUserContext(EmailContext):
    __template_path__: str = "updated_user.html"
    __subject__: str = "One or more of account details have been changed"

    values_updated: dict


@dataclass(kw_only=True)
class ForgotPasswordContext(EmailContext):
    __template_path__: str = "forgot_password.html"
    __subject__: str = "Password Reset Request"

    reset_link: str