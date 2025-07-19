import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_email(subject: str, recipient: str, html_content: str, plaintext_content: str) -> bool:
    """Generic email sending function"""
    try:
        # Email configuration
        sender = os.getenv("EMAIL_SENDER", "skinsage.app@gmail.com")
        password = os.getenv("EMAIL_PASSWORD", "xfmx ihit uzli dlkl")
        smtp_server = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("EMAIL_PORT", 587))
        use_tls = os.getenv("EMAIL_USE_TLS", "True") == "True"
        
        # Validate credentials
        if not sender or not password:
            logger.error("Email credentials not configured")
            return False
            
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"SkinSage <{sender}>"
        msg['To'] = recipient
        
        # Attach both plaintext and HTML versions
        msg.attach(MIMEText(plaintext_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            if use_tls:
                server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        
        logger.info(f"Email sent to {recipient}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Please check your email credentials.")
        return False
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return False

def send_welcome_email(user_email: str, skin_type: str, concerns: list) -> bool:
    """Send welcome email to new user"""
    try:
        # Format concerns
        concerns_str = ", ".join(concerns) if concerns else "no specific concerns"
        current_year = datetime.now().year
        
        # Create HTML content
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6a5acd, #ff7eb9); padding: 40px; text-align: center; color: white; }}
                .content {{ background: #ffffff; padding: 30px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #777; font-size: 0.9em; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #6a5acd; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; }}
                .profile-card {{ background: #f9f9f9; padding: 20px; border-radius: 8px; border-left: 4px solid #6a5acd; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 32px;">✨ Welcome to SkinSage!</h1>
                    <p style="margin: 10px 0 0; font-size: 18px; opacity: 0.9;">Your journey to better skin starts now</p>
                </div>
                
                <div class="content">
                    <p>Hi there,</p>
                    
                    <p>Thank you for joining SkinSage! We're excited to help you achieve your best skin possible.</p>
                    
                    <div class="profile-card">
                        <h3 style="color: #6a5acd; margin-top: 0;">Your Skin Profile</h3>
                        <p><strong>Skin Type:</strong> {skin_type.capitalize()}</p>
                        <p><strong>Skin Concerns:</strong> {concerns_str}</p>
                    </div>
                    
                    <p>Here's what you can do next:</p>
                    <ol>
                        <li>📸 <strong>Analyze products</strong> - Upload ingredient lists for personalized insights</li>
                        <li>✨ <strong>Generate routines</strong> - Get AM/PM routines tailored to your skin</li>
                        <li>💬 <strong>Chat with our assistant</strong> - Get answers to your skincare questions</li>
                    </ol>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://your-app-url.com" class="btn">Get Started with SkinSage</a>
                    </div>
                    
                    <p>We're committed to helping you achieve healthy, glowing skin!</p>
                    
                    <p>Best regards,<br>
                    The SkinSage Team</p>
                </div>
                
                <div class="footer">
                    <p>SkinSage - Personalized Skincare Analysis</p>
                    <p>© {current_year} SkinSage | Your journey to better skin starts here</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plaintext content
        plaintext = f"Welcome to SkinSage!\n\n"
        plaintext += f"Thank you for joining SkinSage! We're excited to help you achieve your best skin possible.\n\n"
        plaintext += f"Your Skin Profile:\n"
        plaintext += f"- Skin Type: {skin_type.capitalize()}\n"
        plaintext += f"- Concerns: {concerns_str}\n\n"
        plaintext += f"Here's what you can do next:\n"
        plaintext += f"1. Analyze products - Upload ingredient lists for personalized insights\n"
        plaintext += f"2. Generate routines - Get AM/PM routines tailored to your skin\n"
        plaintext += f"3. Chat with our assistant - Get answers to your skincare questions\n\n"
        plaintext += f"Get started at: https://your-app-url.com\n\n"
        plaintext += f"Best regards,\nThe SkinSage Team\n\n"
        
        # Send using generic email function
        return send_email(
            subject="✨ Welcome to SkinSage!",
            recipient=user_email,
            html_content=html,
            plaintext_content=plaintext
        )
    except Exception as e:
        logger.error(f"Failed to prepare welcome email: {str(e)}")
        return False

def send_routine_email(user_email: str, skin_type: str, concerns: list, routine_data: dict):
    """Send skincare routine email to user"""
    try:
        # Email configuration
        sender = os.getenv("EMAIL_SENDER", "skinsage.app@gmail.com")
        password = os.getenv("EMAIL_PASSWORD", "xfmx ihit uzli dlkl")
        smtp_server = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("EMAIL_PORT", 587))
        use_tls = os.getenv("EMAIL_USE_TLS", "True") == "True"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "✨ Your New Personalized Skincare Routine"
        msg['From'] = f"SkinSage <{sender}>"
        msg['To'] = user_email
        
        # Create HTML content
        concerns_str = ", ".join(concerns) if concerns else "no specific concerns"
        time_of_day = routine_data["time_of_day"]
        
        # Build routine HTML
        routine_html = ""
        for i, step in enumerate(routine_data["routine"], start=1):
            product_link = step.get("link", "#") or "#"
            brand = step.get("brand", "Unknown Brand")
            routine_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #6a5acd;">
                <h3 style="margin-top: 0; color: #6a5acd;">Step {i}: {step['step'].capitalize()}</h3>
                <p><strong>Product:</strong> {step['product']}</p>
                <p><strong>Brand:</strong> {brand}</p>
                <p><i>{step.get('description', '')}</i></p>
                <p><a href="{product_link}" style="display: inline-block; padding: 8px 15px; background: #6a5acd; color: white; text-decoration: none; border-radius: 4px;">
                    View Product Details
                </a></p>
            </div>
            """
        
        # Create HTML body
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6a5acd, #ff7eb9); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #ffffff; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .footer {{ text-align: center; margin-top: 30px; color: #777; font-size: 0.9em; }}
                .progress-box {{ background: #e6f7ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2196F3; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: #6a5acd; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">✨ Your Personalized Skincare Routine</h1>
                    <p style="margin: 5px 0 0; opacity: 0.9;">Created just for you by SkinSage AI</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #6a5acd; margin-top: 0;">{time_of_day} Routine for {skin_type.capitalize()} Skin</h2>
                    <p>We've created this routine specifically for your skin type and concerns: <strong>{concerns_str}</strong></p>
                    
                    <div style="margin: 30px 0;">
                        {routine_html}
                    </div>
                    
                    <div class="progress-box">
                        <h3 style="color: #2196F3; margin-top: 0;">How's Your Skin Doing?</h3>
                        <p>We'd love to hear about your progress with these concerns:</p>
                        <p><strong>{concerns_str}</strong></p>
                        <p>Reply to this email to share your experience with our skincare specialist!</p>
                        <p style="text-align: center; margin-top: 20px;">
                            <a href="mailto:{sender}" class="btn">Share Your Progress</a>
                        </p>
                    </div>
                    
                    <p style="margin-top: 30px;"><strong>Pro Tip:</strong> For best results, use these products consistently for at least 4 weeks to see visible improvements.</p>
                </div>
                
                <div class="footer">
                    <p>This routine was automatically generated by SkinSage AI</p>
                    <p>You can always access and modify your routines in the SkinSage app</p>
                    <p>© 2025 SkinSage | Personalized Skincare Analysis</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            if use_tls:
                server.starttls()
            server.login(sender, password)
            server.sendmail(sender, user_email, msg.as_string())
        
        logger.info(f"Routine email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False