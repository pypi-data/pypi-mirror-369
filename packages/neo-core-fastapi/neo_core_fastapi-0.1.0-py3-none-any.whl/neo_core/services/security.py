"""Security services for encryption, hashing, and other security operations."""

from typing import Optional, Dict, Any, Union, List
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import jwt
from pydantic import BaseModel

from .base import BaseService, ServiceException
from ..config import CoreSettings


class SecurityException(ServiceException):
    """Security-related exception."""
    pass


class EncryptionError(SecurityException):
    """Encryption/decryption error."""
    pass


class SignatureError(SecurityException):
    """Signature verification error."""
    pass


class TokenError(SecurityException):
    """Token-related error."""
    pass


class EncryptedData(BaseModel):
    """Encrypted data model."""
    data: str  # Base64 encoded encrypted data
    salt: Optional[str] = None  # Base64 encoded salt
    iv: Optional[str] = None  # Base64 encoded initialization vector
    algorithm: str = "fernet"
    created_at: datetime
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class SignedData(BaseModel):
    """Signed data model."""
    data: str
    signature: str
    algorithm: str = "hmac-sha256"
    created_at: datetime
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class SecurityToken(BaseModel):
    """Security token model."""
    token: str
    token_type: str  # jwt, signed, encrypted
    expires_at: Optional[datetime] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class EncryptionService(BaseService):
    """Encryption and decryption service."""
    
    def __init__(self, settings: CoreSettings = None, encryption_key: Optional[str] = None):
        super().__init__(settings)
        
        # Encryption settings
        self.encryption_key = encryption_key or getattr(self.settings, 'ENCRYPTION_KEY', None)
        
        if not self.encryption_key:
            # Generate a new key if none provided
            self.encryption_key = Fernet.generate_key().decode()
            self.logger.warning("No encryption key provided, generated a new one. This should be stored securely.")
        
        # Initialize Fernet cipher
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
        
        self.fernet = Fernet(self.encryption_key)
        
        # Default algorithms
        self.default_hash_algorithm = getattr(self.settings, 'DEFAULT_HASH_ALGORITHM', 'sha256')
        self.default_key_derivation_iterations = getattr(self.settings, 'KEY_DERIVATION_ITERATIONS', 100000)
        
        self.logger.info("Encryption service initialized")
    
    def encrypt_data(self, data: Union[str, bytes], algorithm: str = "fernet") -> EncryptedData:
        """Encrypt data using specified algorithm."""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == "fernet":
                encrypted = self.fernet.encrypt(data)
                return EncryptedData(
                    data=base64.b64encode(encrypted).decode('utf-8'),
                    algorithm=algorithm
                )
            elif algorithm == "aes-256-gcm":
                return self._encrypt_aes_gcm(data)
            else:
                raise EncryptionError(f"Unsupported encryption algorithm: {algorithm}")
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data."""
        try:
            if encrypted_data.algorithm == "fernet":
                encrypted_bytes = base64.b64decode(encrypted_data.data.encode('utf-8'))
                return self.fernet.decrypt(encrypted_bytes)
            elif encrypted_data.algorithm == "aes-256-gcm":
                return self._decrypt_aes_gcm(encrypted_data)
            else:
                raise EncryptionError(f"Unsupported decryption algorithm: {encrypted_data.algorithm}")
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt data: {str(e)}")
    
    def encrypt_string(self, text: str, algorithm: str = "fernet") -> str:
        """Encrypt string and return base64 encoded result."""
        encrypted_data = self.encrypt_data(text, algorithm)
        return encrypted_data.data
    
    def decrypt_string(self, encrypted_text: str, algorithm: str = "fernet") -> str:
        """Decrypt base64 encoded string."""
        encrypted_data = EncryptedData(
            data=encrypted_text,
            algorithm=algorithm
        )
        decrypted_bytes = self.decrypt_data(encrypted_data)
        return decrypted_bytes.decode('utf-8')
    
    def _encrypt_aes_gcm(self, data: bytes) -> EncryptedData:
        """Encrypt data using AES-256-GCM."""
        # Generate random key and IV
        key = secrets.token_bytes(32)  # 256 bits
        iv = secrets.token_bytes(12)   # 96 bits for GCM
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Combine ciphertext and tag
        encrypted_data = ciphertext + encryptor.tag
        
        return EncryptedData(
            data=base64.b64encode(encrypted_data).decode('utf-8'),
            salt=base64.b64encode(key).decode('utf-8'),
            iv=base64.b64encode(iv).decode('utf-8'),
            algorithm="aes-256-gcm"
        )
    
    def _decrypt_aes_gcm(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using AES-256-GCM."""
        if not encrypted_data.salt or not encrypted_data.iv:
            raise EncryptionError("Salt and IV required for AES-256-GCM decryption")
        
        # Decode components
        key = base64.b64decode(encrypted_data.salt.encode('utf-8'))
        iv = base64.b64decode(encrypted_data.iv.encode('utf-8'))
        encrypted_bytes = base64.b64decode(encrypted_data.data.encode('utf-8'))
        
        # Split ciphertext and tag
        ciphertext = encrypted_bytes[:-16]
        tag = encrypted_bytes[-16:]
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def encrypt_with_password(self, data: Union[str, bytes], password: str) -> EncryptedData:
        """Encrypt data with password-based key derivation."""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Generate salt
            salt = secrets.token_bytes(16)
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.default_key_derivation_iterations,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            
            # Encrypt with Fernet
            fernet = Fernet(base64.urlsafe_b64encode(key))
            encrypted = fernet.encrypt(data)
            
            return EncryptedData(
                data=base64.b64encode(encrypted).decode('utf-8'),
                salt=base64.b64encode(salt).decode('utf-8'),
                algorithm="fernet-pbkdf2"
            )
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt with password: {str(e)}")
    
    def decrypt_with_password(self, encrypted_data: EncryptedData, password: str) -> bytes:
        """Decrypt data with password-based key derivation."""
        try:
            if encrypted_data.algorithm != "fernet-pbkdf2":
                raise EncryptionError("Invalid algorithm for password-based decryption")
            
            if not encrypted_data.salt:
                raise EncryptionError("Salt required for password-based decryption")
            
            # Decode salt
            salt = base64.b64decode(encrypted_data.salt.encode('utf-8'))
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.default_key_derivation_iterations,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            
            # Decrypt with Fernet
            fernet = Fernet(base64.urlsafe_b64encode(key))
            encrypted_bytes = base64.b64decode(encrypted_data.data.encode('utf-8'))
            return fernet.decrypt(encrypted_bytes)
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt with password: {str(e)}")


class HashingService(BaseService):
    """Hashing and signature service."""
    
    def __init__(self, settings: CoreSettings = None, secret_key: Optional[str] = None):
        super().__init__(settings)
        
        # Secret key for HMAC
        self.secret_key = secret_key or getattr(self.settings, 'SECRET_KEY', None)
        
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
            self.logger.warning("No secret key provided, generated a new one. This should be stored securely.")
        
        if isinstance(self.secret_key, str):
            self.secret_key = self.secret_key.encode('utf-8')
        
        self.logger.info("Hashing service initialized")
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Hash data using specified algorithm."""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == "md5":
                hash_obj = hashlib.md5(data)
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1(data)
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256(data)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data)
            else:
                raise SecurityException(f"Unsupported hash algorithm: {algorithm}")
            
            return hash_obj.hexdigest()
        except Exception as e:
            raise SecurityException(f"Failed to hash data: {str(e)}")
    
    def sign_data(self, data: Union[str, bytes], algorithm: str = "hmac-sha256") -> SignedData:
        """Sign data using specified algorithm."""
        try:
            if isinstance(data, str):
                data_str = data
                data_bytes = data.encode('utf-8')
            else:
                data_str = data.decode('utf-8')
                data_bytes = data
            
            if algorithm == "hmac-sha256":
                signature = hmac.new(
                    self.secret_key,
                    data_bytes,
                    hashlib.sha256
                ).hexdigest()
            elif algorithm == "hmac-sha512":
                signature = hmac.new(
                    self.secret_key,
                    data_bytes,
                    hashlib.sha512
                ).hexdigest()
            else:
                raise SignatureError(f"Unsupported signature algorithm: {algorithm}")
            
            return SignedData(
                data=data_str,
                signature=signature,
                algorithm=algorithm
            )
        except Exception as e:
            raise SignatureError(f"Failed to sign data: {str(e)}")
    
    def verify_signature(self, signed_data: SignedData) -> bool:
        """Verify data signature."""
        try:
            # Re-sign the data
            new_signed = self.sign_data(signed_data.data, signed_data.algorithm)
            
            # Compare signatures using constant-time comparison
            return hmac.compare_digest(signed_data.signature, new_signed.signature)
        except Exception as e:
            self.logger.error(f"Failed to verify signature: {str(e)}")
            return False
    
    def generate_checksum(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Generate checksum for data integrity verification."""
        return self.hash_data(data, algorithm)
    
    def verify_checksum(self, data: Union[str, bytes], checksum: str, algorithm: str = "sha256") -> bool:
        """Verify data integrity using checksum."""
        try:
            calculated_checksum = self.generate_checksum(data, algorithm)
            return hmac.compare_digest(checksum, calculated_checksum)
        except Exception as e:
            self.logger.error(f"Failed to verify checksum: {str(e)}")
            return False


class TokenService(BaseService):
    """Token generation and verification service."""
    
    def __init__(self, settings: CoreSettings = None, secret_key: Optional[str] = None):
        super().__init__(settings)
        
        # Secret key for JWT
        self.secret_key = secret_key or getattr(self.settings, 'JWT_SECRET_KEY', None)
        
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
            self.logger.warning("No JWT secret key provided, generated a new one. This should be stored securely.")
        
        # JWT settings
        self.jwt_algorithm = getattr(self.settings, 'JWT_ALGORITHM', 'HS256')
        self.jwt_expiration = getattr(self.settings, 'JWT_EXPIRATION_SECONDS', 3600)
        
        # Initialize hashing service for signed tokens
        self.hashing_service = HashingService(settings, secret_key)
        
        self.logger.info("Token service initialized")
    
    def generate_jwt_token(
        self,
        payload: Dict[str, Any],
        expires_in: Optional[int] = None,
        algorithm: Optional[str] = None
    ) -> SecurityToken:
        """Generate JWT token."""
        try:
            # Set expiration
            expires_in = expires_in or self.jwt_expiration
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Add standard claims
            jwt_payload = payload.copy()
            jwt_payload.update({
                'iat': datetime.utcnow(),
                'exp': expires_at,
                'jti': secrets.token_urlsafe(16)  # JWT ID
            })
            
            # Generate token
            algorithm = algorithm or self.jwt_algorithm
            token = jwt.encode(jwt_payload, self.secret_key, algorithm=algorithm)
            
            return SecurityToken(
                token=token,
                token_type="jwt",
                expires_at=expires_at,
                metadata={
                    'algorithm': algorithm,
                    'payload_keys': list(payload.keys())
                }
            )
        except Exception as e:
            raise TokenError(f"Failed to generate JWT token: {str(e)}")
    
    def verify_jwt_token(self, token: str, algorithm: Optional[str] = None) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            algorithm = algorithm or self.jwt_algorithm
            payload = jwt.decode(token, self.secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise TokenError(f"Failed to verify JWT token: {str(e)}")
    
    def generate_signed_token(
        self,
        payload: Dict[str, Any],
        expires_in: Optional[int] = None
    ) -> SecurityToken:
        """Generate signed token (non-JWT)."""
        try:
            # Set expiration
            expires_in = expires_in or self.jwt_expiration
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Create token payload
            token_payload = {
                'data': payload,
                'exp': expires_at.timestamp(),
                'jti': secrets.token_urlsafe(16)
            }
            
            # Encode and sign
            token_data = json.dumps(token_payload, default=str)
            signed_data = self.hashing_service.sign_data(token_data)
            
            # Create token (base64 encoded)
            token_dict = {
                'data': signed_data.data,
                'signature': signed_data.signature,
                'algorithm': signed_data.algorithm
            }
            token = base64.b64encode(json.dumps(token_dict).encode()).decode()
            
            return SecurityToken(
                token=token,
                token_type="signed",
                expires_at=expires_at,
                metadata={
                    'algorithm': signed_data.algorithm,
                    'payload_keys': list(payload.keys())
                }
            )
        except Exception as e:
            raise TokenError(f"Failed to generate signed token: {str(e)}")
    
    def verify_signed_token(self, token: str) -> Dict[str, Any]:
        """Verify signed token."""
        try:
            # Decode token
            token_dict = json.loads(base64.b64decode(token.encode()).decode())
            
            # Create signed data object
            signed_data = SignedData(
                data=token_dict['data'],
                signature=token_dict['signature'],
                algorithm=token_dict['algorithm']
            )
            
            # Verify signature
            if not self.hashing_service.verify_signature(signed_data):
                raise TokenError("Invalid token signature")
            
            # Parse payload
            payload = json.loads(signed_data.data)
            
            # Check expiration
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if datetime.utcnow().timestamp() > exp_timestamp:
                    raise TokenError("Token has expired")
            
            return payload.get('data', {})
        except json.JSONDecodeError:
            raise TokenError("Invalid token format")
        except Exception as e:
            raise TokenError(f"Failed to verify signed token: {str(e)}")
    
    def generate_random_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, prefix: str = "neo", length: int = 32) -> str:
        """Generate API key with prefix."""
        random_part = secrets.token_urlsafe(length)
        return f"{prefix}_{random_part}"
    
    def refresh_jwt_token(self, token: str) -> SecurityToken:
        """Refresh JWT token if it's still valid."""
        try:
            # Verify current token
            payload = self.verify_jwt_token(token)
            
            # Remove standard claims
            user_payload = {k: v for k, v in payload.items() 
                          if k not in ['iat', 'exp', 'jti']}
            
            # Generate new token
            return self.generate_jwt_token(user_payload)
        except Exception as e:
            raise TokenError(f"Failed to refresh token: {str(e)}")


class SecurityService(BaseService):
    """Main security service combining all security operations."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        
        # Initialize sub-services
        self.encryption = EncryptionService(settings)
        self.hashing = HashingService(settings)
        self.tokens = TokenService(settings)
        
        # Security settings
        self.password_min_length = getattr(self.settings, 'PASSWORD_MIN_LENGTH', 8)
        self.password_require_uppercase = getattr(self.settings, 'PASSWORD_REQUIRE_UPPERCASE', True)
        self.password_require_lowercase = getattr(self.settings, 'PASSWORD_REQUIRE_LOWERCASE', True)
        self.password_require_digits = getattr(self.settings, 'PASSWORD_REQUIRE_DIGITS', True)
        self.password_require_special = getattr(self.settings, 'PASSWORD_REQUIRE_SPECIAL', True)
        
        self.logger.info("Security service initialized")
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        issues = []
        
        # Length check
        if len(password) < self.password_min_length:
            issues.append(f"Password must be at least {self.password_min_length} characters long")
        
        # Character requirements
        if self.password_require_uppercase and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if self.password_require_lowercase and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if self.password_require_digits and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        if self.password_require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                issues.append("Password must contain at least one special character")
        
        # Common password check (basic)
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890"
        ]
        if password.lower() in common_passwords:
            issues.append("Password is too common")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "strength": self._calculate_password_strength(password)
        }
    
    def generate_secure_password(self, length: int = 12) -> str:
        """Generate cryptographically secure password."""
        import string
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each required set
        password = []
        
        if self.password_require_lowercase:
            password.append(secrets.choice(lowercase))
        if self.password_require_uppercase:
            password.append(secrets.choice(uppercase))
        if self.password_require_digits:
            password.append(secrets.choice(digits))
        if self.password_require_special:
            password.append(secrets.choice(special))
        
        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength score."""
        score = 0
        
        # Length bonus
        score += min(len(password) * 2, 20)
        
        # Character variety bonus
        if any(c.islower() for c in password):
            score += 5
        if any(c.isupper() for c in password):
            score += 5
        if any(c.isdigit() for c in password):
            score += 5
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 10
        
        # Uniqueness bonus
        unique_chars = len(set(password))
        score += min(unique_chars * 2, 20)
        
        # Pattern penalties
        if password.lower() in password or password.upper() in password:
            score -= 10
        
        # Determine strength
        if score >= 80:
            return "very_strong"
        elif score >= 60:
            return "strong"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "weak"
        else:
            return "very_weak"
    
    def sanitize_input(self, text: str, allow_html: bool = False) -> str:
        """Sanitize user input to prevent XSS and injection attacks."""
        if not allow_html:
            # Remove HTML tags
            import re
            text = re.sub(r'<[^>]+>', '', text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, expected_token: str) -> bool:
        """Verify CSRF token."""
        return hmac.compare_digest(token, expected_token)
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    def audit_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "info"
    ) -> None:
        """Audit security events."""
        log_data = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        if severity == "critical":
            self.logger.critical(f"Security event: {json.dumps(log_data)}")
        elif severity == "error":
            self.logger.error(f"Security event: {json.dumps(log_data)}")
        elif severity == "warning":
            self.logger.warning(f"Security event: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Security event: {json.dumps(log_data)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check security service health."""
        try:
            # Test encryption
            test_data = "test_data"
            encrypted = self.encryption.encrypt_string(test_data)
            decrypted = self.encryption.decrypt_string(encrypted)
            encryption_ok = decrypted == test_data
            
            # Test hashing
            test_hash = self.hashing.hash_data(test_data)
            hashing_ok = len(test_hash) > 0
            
            # Test token generation
            test_token = self.tokens.generate_jwt_token({"test": "data"})
            token_payload = self.tokens.verify_jwt_token(test_token.token)
            tokens_ok = token_payload.get("test") == "data"
            
            is_healthy = all([encryption_ok, hashing_ok, tokens_ok])
            
            return {
                "healthy": is_healthy,
                "checks": {
                    "encryption": encryption_ok,
                    "hashing": hashing_ok,
                    "tokens": tokens_ok
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }