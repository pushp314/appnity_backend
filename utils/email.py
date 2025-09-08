from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_html_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Send HTML email with text fallback
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Render HTML content
    html_content = render_to_string(f'emails/{template_name}.html', context)
    
    # Create text content by stripping HTML
    text_content = strip_tags(html_content)
    
    # Create email message
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )
    
    # Attach HTML content
    msg.attach_alternative(html_content, "text/html")
    
    # Send email
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_welcome_email(user_email, user_name):
    """
    Send welcome email to new users
    """
    subject = 'Welcome to Appnity! 🚀'
    context = {
        'user_name': user_name,
        'company_name': 'Appnity Software Private Limited',
        'website_url': 'https://appnity.co.in',
        'support_email': 'hello@appnity.co.in'
    }
    
    return send_html_email(
        subject=subject,
        template_name='welcome',
        context=context,
        recipient_list=[user_email]
    )


def send_contact_notification(contact_data):
    """
    Send contact form notification to admin
    """
    subject = f'New Contact Form Submission - {contact_data["inquiry_type"]}'
    context = {
        'contact': contact_data,
        'admin_url': f'{settings.SITE_URL}/admin/contacts/contact/{contact_data["id"]}/'
    }
    
    return send_html_email(
        subject=subject,
        template_name='contact_notification',
        context=context,
        recipient_list=[settings.DEFAULT_FROM_EMAIL]
    )


def send_newsletter_welcome(email):
    """
    Send newsletter welcome email
    """
    subject = 'Welcome to Appnity Newsletter! 🚀'
    context = {
        'email': email,
        'unsubscribe_url': f'{settings.SITE_URL}/newsletter/unsubscribe/',
        'website_url': 'https://appnity.co.in'
    }
    
    return send_html_email(
        subject=subject,
        template_name='newsletter_welcome',
        context=context,
        recipient_list=[email]
    )