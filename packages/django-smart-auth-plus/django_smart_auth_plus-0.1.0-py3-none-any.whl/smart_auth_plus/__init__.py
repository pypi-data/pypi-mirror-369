__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .models import SmartUser
from .otp.sms_email import generate_otp, send_sms, send_email
from .social.providers import GoogleAuth, GitHubAuth
from .permissions import has_role

__all__ = [
    "SmartUser",
    "generate_otp",
    "send_sms",
    "send_email",
    "GoogleAuth",
    "GitHubAuth",
    "has_role",
]
