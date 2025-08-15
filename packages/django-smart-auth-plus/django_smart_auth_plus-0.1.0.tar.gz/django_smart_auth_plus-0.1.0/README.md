# django-smart-auth-plus

Advanced Django Authentication package.

## Features
- Multi-factor authentication (SMS/Email OTP)
- Social login (Google, GitHub, Facebook)
- Role-based permissions
- JWT + Session support
- Password policies
- Audit logs

## Installation
```bash
pip install django-smart-auth-plus
```

## Usage

### User model
```python
from smart_auth_plus.models import SmartUser
```

### OTP
```python
from smart_auth_plus import generate_otp, send_sms, send_email
```

### Social Login
```python
from smart_auth_plus import GoogleAuth, GitHubAuth
```

### Role check
```python
from smart_auth_plus import has_role
```
