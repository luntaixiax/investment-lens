import asyncio
from jinja2 import Environment, FileSystemLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP
from src.app.utils.secrets import get_secret
from src.app.model.exceptions import UnexpectedError

env = Environment(loader=FileSystemLoader("src/app/service/templates"))


class EmailService:
    
    def render_body(self, template_name: str, context: dict) -> str:
        template = env.get_template(template_name)
        return template.render(**context)

    async def send_email(self, to_email: str, subject: str, html_body: str):
        secret = await asyncio.to_thread(get_secret)
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = secret['mailbox']['email']
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        # Standard way for SSL (port 465): use_tls=True establishes SSL from the start
        # This is equivalent to smtplib.SMTP_SSL
        # Add timeouts to prevent hanging connections (10 seconds)
        try:
            async with SMTP(
                hostname=secret['mailbox']['smtp_server'],
                port=int(secret['mailbox']['smtp_port']),
                username=secret['mailbox']['email'],
                password=secret['mailbox']['password'], 
                use_tls=True,  # SSL/TLS from the start (for port 465)
                timeout=10  # Connection timeout in seconds
            ) as smtp:
                # Context manager handles connection, but we can call connect explicitly with timeout
                await smtp.send_message(msg)
        except Exception as e:
            raise UnexpectedError(f"Failed to send email: {e}")