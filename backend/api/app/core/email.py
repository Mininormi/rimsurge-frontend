"""
SMTP 邮件发送功能
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from typing import Optional
from app.config import settings


def send_verification_code_email(to_email: str, code: str, scene: str = "register") -> bool:
    """
    发送邮箱验证码邮件
    
    Args:
        to_email: 收件人邮箱
        code: 6位验证码
        scene: 场景（register/reset）
    
    Returns:
        是否发送成功
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False
    
    try:
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        # 使用 formataddr 和 Header 正确编码包含中文的邮件头
        # Header 对象需要转换为字符串才能用于邮件头
        from_name_header = Header(settings.SMTP_FROM_NAME, 'utf-8')
        msg['From'] = formataddr((str(from_name_header), settings.SMTP_FROM_EMAIL))
        msg['To'] = to_email
        # 根据场景设置邮件主题和内容
        if scene == "reset":
            subject_text = "RimSurge 密码重置验证码"
            action_text = "重置密码"
            description_text = "您正在重置 RimSurge 账号密码，请使用以下验证码完成验证："
        else:
            subject_text = "RimSurge 邮箱验证码"
            action_text = "注册账号"
            description_text = "您正在注册 RimSurge 账号，请使用以下验证码完成验证："
        
        subject_header = Header(subject_text, 'utf-8')
        msg['Subject'] = str(subject_header)
        
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
                    <h2>{subject_text}</h2>
                    <p>您好！</p>
                    <p>{description_text}</p>
                    
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
        {subject_text}
        
        您好！
        
        {description_text}
        
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
        use_ssl = smtp_port == 465  # 端口 465 使用 SMTP_SSL
        use_tls = smtp_port == 587  # 端口 587 使用 STARTTLS
        
        # 使用 sendmail 方法代替 send_message，确保编码正确处理
        # sendmail 方法可以更好地处理包含中文的邮件头
        from_email_addr = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        
        if use_ssl:
            # 使用 SMTP_SSL（端口 465）
            with smtplib.SMTP_SSL(settings.SMTP_HOST, smtp_port) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                # 使用 sendmail 方法，msg.as_string() 会自动处理编码
                server.sendmail(from_email_addr, [to_email], msg.as_string())
        else:
            # 使用 SMTP + STARTTLS（端口 587）
            with smtplib.SMTP(settings.SMTP_HOST, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                # 使用 sendmail 方法，msg.as_string() 会自动处理编码
                server.sendmail(from_email_addr, [to_email], msg.as_string())
        
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def send_account_exists_notification_email(to_email: str) -> bool:
    """
    发送账号已存在提示邮件（注册场景，邮箱已存在时）
    
    Args:
        to_email: 收件人邮箱
    
    Returns:
        是否发送成功
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False
    
    try:
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        from_name_header = Header(settings.SMTP_FROM_NAME, 'utf-8')
        msg['From'] = formataddr((str(from_name_header), settings.SMTP_FROM_EMAIL))
        msg['To'] = to_email
        subject_header = Header("RimSurge 账号提示", 'utf-8')
        msg['Subject'] = str(subject_header)
        
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
                .info {{
                    background-color: #e8f4f8;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
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
                    <h2>RimSurge 账号提示</h2>
                    <p>您好！</p>
                    <div class="info">
                        <p>您尝试注册的邮箱 <strong>{to_email}</strong> 已经存在账号。</p>
                        <p>如果您忘记密码，请使用"找回密码"功能。</p>
                    </div>
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
        RimSurge 账号提示
        
        您好！
        
        您尝试注册的邮箱 {to_email} 已经存在账号。
        如果您忘记密码，请使用"找回密码"功能。
        
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
        use_ssl = smtp_port == 465
        use_tls = smtp_port == 587
        from_email_addr = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        
        if use_ssl:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, smtp_port) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(from_email_addr, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(settings.SMTP_HOST, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(from_email_addr, [to_email], msg.as_string())
        
        return True
    except Exception as e:
        print(f"发送提示邮件失败: {e}")
        return False
