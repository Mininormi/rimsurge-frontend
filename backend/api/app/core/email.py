"""
SMTP 邮件发送功能
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings


def send_verification_code_email(to_email: str, code: str) -> bool:
    """
    发送邮箱验证码邮件
    
    Args:
        to_email: 收件人邮箱
        code: 6位验证码
    
    Returns:
        是否发送成功
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False
    
    try:
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = "RimSurge 邮箱验证码"
        
        # HTML 邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
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
                    background-color: #f9f9f9;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .code-box {{
                    background-color: #f4f4f4;
                    border: 2px dashed #333;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    color: #333;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    color: #e74c3c;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #999;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>RimSurge 邮箱验证码</h2>
                    <p>您好！</p>
                    <p>您正在注册 RimSurge 账号，请使用以下验证码完成验证：</p>
                    
                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>
                    
                    <p class="warning">⚠️ 验证码有效期为 5 分钟，请及时使用。</p>
                    <p>如果这不是您的操作，请忽略此邮件。</p>
                    
                    <div class="footer">
                        <p>此邮件由 RimSurge 系统自动发送，请勿回复。</p>
                        <p>© 2024 RimSurge. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本内容（备用）
        text_content = f"""
        RimSurge 邮箱验证码
        
        您好！
        
        您正在注册 RimSurge 账号，请使用以下验证码完成验证：
        
        验证码：{code}
        
        验证码有效期为 5 分钟，请及时使用。
        
        如果这不是您的操作，请忽略此邮件。
        
        ---
        此邮件由 RimSurge 系统自动发送，请勿回复。
        © 2024 RimSurge. All rights reserved.
        """
        
        # 添加文本和 HTML 内容
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # 发送邮件
        smtp_port = settings.SMTP_PORT or 587
        use_tls = smtp_port == 587
        
        with smtplib.SMTP(settings.SMTP_HOST, smtp_port) as server:
            if use_tls:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False
