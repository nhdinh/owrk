"""
Email Service for sending emails
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails via SMTP
    """

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = to_email

            # Attach text part
            text_part = MIMEText(body_text, "plain")
            msg.attach(text_part)

            # Attach HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, "html")
                msg.attach(html_part)

            # Check if SMTP is configured
            if not settings.SMTP_HOST or not settings.SMTP_USER:
                logger.warning(
                    f"SMTP not configured. Would send email to {to_email}: {subject}"
                )
                logger.info(f"Email body:\n{body_text}")
                return True  # Return True in dev mode to not block flow

            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()

                if settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

                server.send_message(msg)
                logger.info(f"Email sent successfully to {to_email}")
                return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(
        to_email: str, reset_token: str, user_full_name: str
    ) -> bool:
        """
        Send password reset email with token

        Args:
            to_email: User email
            reset_token: Password reset token
            user_full_name: User's full name

        Returns:
            True if sent successfully
        """
        # In production, this should be a proper frontend URL
        # For now, we'll use the API endpoint directly for testing
        reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"

        subject = "Password Reset Request - Asset Management System"

        # Plain text body
        body_text = f"""
Hello {user_full_name},

You have requested to reset your password for the Asset Management System.

Please use the following token to reset your password:
{reset_token}

Or click the link below to reset your password:
{reset_link}

This token will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
Asset Management System Team
        """.strip()

        # HTML body
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4F46E5;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9fafb;
            padding: 30px;
            border: 1px solid #e5e7eb;
            border-top: none;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #4F46E5;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .token-box {{
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            word-break: break-all;
            margin: 15px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        <div class="content">
            <p>Hello {user_full_name},</p>

            <p>You have requested to reset your password for the Asset Management System.</p>

            <p>Click the button below to reset your password:</p>

            <div style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>

            <p>Or copy and paste this token into the password reset form:</p>

            <div class="token-box">
                {reset_token}
            </div>

            <p><strong>This token will expire in 1 hour.</strong></p>

            <p>If you did not request a password reset, please ignore this email.</p>

            <p>Best regards,<br>Asset Management System Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return EmailService.send_email(to_email, subject, body_text, body_html)

    @staticmethod
    def send_password_changed_notification(
        to_email: str, user_full_name: str
    ) -> bool:
        """
        Send notification that password was changed successfully

        Args:
            to_email: User email
            user_full_name: User's full name

        Returns:
            True if sent successfully
        """
        subject = "Password Changed - Asset Management System"

        body_text = f"""
Hello {user_full_name},

Your password for the Asset Management System has been successfully changed.

If you did not make this change, please contact your system administrator immediately.

Best regards,
Asset Management System Team
        """.strip()

        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #10b981;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9fafb;
            padding: 30px;
            border: 1px solid #e5e7eb;
            border-top: none;
        }}
        .alert {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Changed Successfully</h1>
        </div>
        <div class="content">
            <p>Hello {user_full_name},</p>

            <p>Your password for the Asset Management System has been successfully changed.</p>

            <div class="alert">
                <strong>Security Notice:</strong><br>
                If you did not make this change, please contact your system administrator immediately.
            </div>

            <p>Best regards,<br>Asset Management System Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return EmailService.send_email(to_email, subject, body_text, body_html)
