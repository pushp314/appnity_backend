import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format
    """
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise ValidationError(
            _('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
        )


def validate_file_size(value):
    """
    Validate file size (max 5MB)
    """
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_('File size cannot exceed 5MB'))


def validate_image_file(value):
    """
    Validate image file type and size
    """
    # Check file size
    validate_file_size(value)
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if value.content_type not in allowed_types:
        raise ValidationError(_('Only JPEG, PNG, GIF, and WebP images are allowed'))


def validate_document_file(value):
    """
    Validate document file type and size
    """
    # Check file size
    validate_file_size(value)
    
    # Check file type
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    if value.content_type not in allowed_types:
        raise ValidationError(_('Only PDF and Word documents are allowed'))


def validate_url_slug(value):
    """
    Validate URL slug format
    """
    slug_regex = re.compile(r'^[-a-zA-Z0-9_]+$')
    if not slug_regex.match(value):
        raise ValidationError(
            _('Slug can only contain letters, numbers, hyphens, and underscores')
        )


def validate_hex_color(value):
    """
    Validate hex color code
    """
    hex_regex = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    if not hex_regex.match(value):
        raise ValidationError(_('Enter a valid hex color code (e.g., #FF0000)'))