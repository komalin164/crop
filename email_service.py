"""Send OTP via SMTP with HTML template."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USE_TLS,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER,
)


def _otp_html_template(otp: str, name: str = "") -> str:
    """HTML email template for OTP."""
    greeting = f"Hi {name}," if name else "Hi,"
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crop Suitability - OTP</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 480px; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">
          <tr>
            <td style="background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); padding: 32px 24px; text-align: center;">
              <span style="font-size: 48px;">🌾</span>
              <h1 style="margin: 12px 0 0 0; color: #ffffff; font-size: 22px; font-weight: 600;">Crop Suitability</h1>
              <p style="margin: 4px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">Your Agriculture Advisor</p>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 24px;">
              <p style="margin: 0 0 16px 0; color: #333; font-size: 16px; line-height: 1.5;">{greeting}</p>
              <p style="margin: 0 0 24px 0; color: #555; font-size: 15px; line-height: 1.5;">Your one-time password (OTP) to access the Crop Suitability app is:</p>
              <div style="background: #f0f7f0; border: 2px dashed #2E7D32; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <span style="font-size: 28px; font-weight: 700; letter-spacing: 8px; color: #1B5E20;">{otp}</span>
              </div>
              <p style="margin: 0 0 8px 0; color: #888; font-size: 13px;">Valid for 5 minutes. Do not share this code.</p>
              <p style="margin: 24px 0 0 0; color: #555; font-size: 14px;">Welcome to Crop Suitability! We're here to help you with crop recommendations, fertilizer advice, irrigation schedules, and more.</p>
            </td>
          </tr>
          <tr>
            <td style="padding: 16px 24px; background: #f9f9f9; text-align: center;">
              <p style="margin: 0; color: #888; font-size: 12px;">© Crop Suitability · Andhra Pradesh & Telangana</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_otp_email(to_email: str, otp: str, name: str = "") -> bool:
    """Send OTP to email with HTML template. Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = MAIL_DEFAULT_SENDER
        msg["To"] = to_email
        msg["Subject"] = "Your Crop Suitability OTP"
        plain = f"Your OTP for Crop Suitability app is: {otp}\n\nValid for 5 minutes. Do not share this code."
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(_otp_html_template(otp, name), "html"))
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False
