from pathlib import Path
from typing import Optional
from datetime import date

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel, AnyHttpUrl
from config.env import env

config = ConnectionConfig(
    MAIL_USERNAME=env.MAIL_USERNAME,
    MAIL_PASSWORD=env.MAIL_PASSWORD,
    MAIL_FROM=env.MAIL_FROM,
    MAIL_SERVER=env.MAIL_SERVER,
    MAIL_FROM_NAME=env.MAIL_FROM_NAME,
    MAIL_PORT=env.MAIL_SSL,
    MAIL_TLS=False,
    MAIL_SSL=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates/email',
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class Email(BaseModel):
    name: str
    message: Optional[str]
    title: str
    company: str = env.BRAND_NAME
    subject: str
    fast_mail: FastMail = FastMail(config)
    template_name: str = "base.html"
    subtype: str = "html"
    recipients: list[EmailStr]

    class Config:
        arbitrary_types_allowed = True
        fields = {"template_name": {"exclude": True}, "subject": {"exclude": True}, "subtype": {"exclude": True}, "fast_mail": {"exclude": True}}

    def create_message(self):
        return MessageSchema(
            subject=self.subject,
            recipients=self.recipients,
            template_body=self.dict(),
            subtype=self.subtype
        )

    async def send(self) -> bool:
        try:
            msg = self.create_message()
            await self.fast_mail.send_message(msg, template_name=self.template_name)
            return True
        except Exception:
            return False


class VerificationEmail(Email):
    title = "Account Verification"
    subject = "Account Verification"
    template_name = 'verification.html'
    link: AnyHttpUrl


class DepositConfirmationEmail(Email):
    title = "Deposit Confirmation"
    subject = "Deposit Confirmation"
    amount: float
    deposit_id: int
    plan: str
    payment_date: date
    due_date: date
    template_name = 'deposit_confirmation.html'


class DepositReceivedEmail(Email):
    title = "Deposit Received"
    subject = "Deposit Received"
    amount: float
    plan: str
    template_name = 'deposit_received.html'


class AccountAlertEmail(Email):
    title = "Credit Alert"
    subject = "Credit Alert"


class WithdrawalEmail(Email):
    title = "Request for Withdrawal"
    subject = "Request for Withdrawal"
    amount: float
    # template_name = "withdrawal.html"


class ReferralEmail(Email):
    title = "Referral Paid"
    subject = "Payment Notification"


class PasswordResetEmail(Email):
    title = "Password Reset"
    subject = "Password Reset"
    link: AnyHttpUrl
    template_name = "password_reset.html"
