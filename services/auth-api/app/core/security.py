"""
Security utilities - JWT, Password Hashing, MFA/OTP
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import qrcode
import io
import base64
import secrets
import string

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_SALT_ROUNDS
)


# ==================== PASSWORD UTILITIES ====================


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT TOKEN UTILITIES ====================


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token

    Args:
        data: Payload data (should include user_id, email, etc.)
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token

    Args:
        data: Payload data
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_temp_token(data: Dict[str, Any], expires_minutes: int = 5) -> str:
    """
    Create temporary token for MFA verification

    Args:
        data: Payload data
        expires_minutes: Token expiration in minutes (default 5)

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "temp"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"JWT decode error: {str(e)}")
        logger.error(
            f"Token (first 20 chars): {token[:20] if len(token) > 20 else token}"
        )
        logger.error(f"JWT_SECRET (first 10 chars): {settings.JWT_SECRET[:10]}...")
        logger.error(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Verify token type (access, refresh, temp)

    Args:
        token: JWT token string
        expected_type: Expected token type

    Returns:
        True if token type matches
    """
    payload = decode_token(token)
    if not payload:
        return False
    return payload.get("type") == expected_type


# ==================== MFA/OTP UTILITIES ====================


def generate_totp_secret() -> str:
    """
    Generate a random base32 secret for TOTP

    Returns:
        Base32 encoded secret
    """
    return pyotp.random_base32()


def generate_totp_uri(secret: str, email: str) -> str:
    """
    Generate TOTP provisioning URI for QR code

    Args:
        secret: TOTP secret
        email: User email

    Returns:
        TOTP URI string
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name=settings.MFA_ISSUER)
    return uri


def generate_qr_code(uri: str) -> str:
    """
    Generate QR code image from TOTP URI

    Args:
        uri: TOTP provisioning URI

    Returns:
        Base64 encoded QR code image
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, otp_code: str, window: int = 1) -> bool:
    """
    Verify TOTP code

    Args:
        secret: TOTP secret
        otp_code: OTP code from user
        window: Time window for verification (default 1 = ±30 seconds)

    Returns:
        True if OTP is valid
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code, valid_window=window)


def generate_backup_codes(count: int = 10) -> list[str]:
    """
    Generate backup codes for MFA recovery

    Args:
        count: Number of backup codes to generate

    Returns:
        List of backup codes
    """
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
        )
        # Format as XXXX-XXXX for readability
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def hash_backup_code(code: str) -> str:
    """
    Hash backup code for storage

    Args:
        code: Backup code

    Returns:
        Hashed code
    """
    return hash_password(code)


def verify_backup_code(code: str, hashed_code: str) -> bool:
    """
    Verify backup code

    Args:
        code: Backup code from user
        hashed_code: Hashed code from database

    Returns:
        True if code matches
    """
    return verify_password(code, hashed_code)


# ==================== PASSWORD RESET TOKEN ====================


def generate_reset_token() -> str:
    """
    Generate secure random token for password reset

    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)


# ==================== UTILITY FUNCTIONS ====================


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random strong password

    Args:
        length: Password length (default 12)

    Returns:
        Random password
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    return password
