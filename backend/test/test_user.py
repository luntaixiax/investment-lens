import os
import pytest
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.app.utils.secrets import get_secret
from src.app.service.email import EmailService

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("ENV") == 'dev', reason="Skipping email service test")
async def test_email_service_send_email():
    """Test EmailService.send_email method."""
    
    email_service = EmailService()

    html = email_service.render_body(
      "reset_email.html", 
      context={"token": 'v9ZHUvhLK6YtytiJJFoFeUY2jeZKCVpDFyprruzw7VfgQXbjPrrQrzb25b8FhRpM'}
    )
    with open("src/app/service/templates/test.html", "w") as f:
        f.write(html)
    
    await email_service.send_email(
        to_email="ailunqian124@gmail.com",
        subject="Reset Your Password",
        html_body=html
    )
