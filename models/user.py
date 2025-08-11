from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from models.runner import Base

class User(Base):
    __tablename__ = 'users'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Unique identifier (UUID)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Authentication fields
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='user', nullable=False)

    # Personal information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    full_name = Column(String(100), nullable=True)

    # Profile information
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Email verification
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_token = Column(String(255), nullable=True)

    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Account security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)

    # Preferences
    timezone = Column(String(50), default='UTC', nullable=True)
    language = Column(String(10), default='en', nullable=True)
    theme = Column(String(20), default='light', nullable=True)

    # Additional constraints
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('username', name='uq_user_username'),
    )

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)

        # Set optional fields
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.phone_number = kwargs.get('phone_number')
        self.bio = kwargs.get('bio')
        self.timezone = kwargs.get('timezone', 'UTC')
        self.language = kwargs.get('language', 'en')

        # Generate full name if first and last names are provided
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)

    def is_account_locked(self):
        """Check if the account is currently locked."""
        if self.account_locked_until:
            from datetime import datetime, timezone
            return datetime.now(timezone.utc) < self.account_locked_until
        return False

    def verify_email(self):
        """Mark the user's email as verified."""
        from datetime import datetime, timezone
        self.is_verified = True
        self.email_verified_at = datetime.now(timezone.utc)
        self.verification_token = None

    def generate_verification_token(self):
        """Generate a new email verification token."""
        import secrets
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token

    def generate_reset_token(self, expires_in=3600):
        """Generate a password reset token that expires in `expires_in` seconds."""
        import secrets
        from datetime import datetime, timezone, timedelta

        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return self.reset_token

    def is_reset_token_valid(self, token):
        """Check if the provided reset token is valid and not expired."""
        if not self.reset_token or self.reset_token != token:
            return False

        if self.reset_token_expires:
            from datetime import datetime, timezone
            return datetime.now(timezone.utc) < self.reset_token_expires

        return False

    def increment_failed_login(self, max_attempts=5, lockout_duration=1800):
        """Increment failed login attempts and lock account if threshold is reached."""
        self.failed_login_attempts += 1

        if self.failed_login_attempts >= max_attempts:
            from datetime import datetime, timezone, timedelta
            self.account_locked_until = datetime.now(timezone.utc) + timedelta(seconds=lockout_duration)

    def reset_failed_login_attempts(self):
        """Reset failed login attempts and unlock account."""
        self.failed_login_attempts = 0
        self.account_locked_until = None

    def update_last_login(self):
        """Update the last login timestamp."""
        from datetime import datetime, timezone
        self.last_login = datetime.now(timezone.utc)

    def get_uuid(self):
        """Get the UUID of the user."""
        return self.uuid

    def to_dict(self, include_sensitive=False):
        """Convert user object to dictionary."""
        user_dict = {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None,
            'last_login': self.last_login if self.last_login else None,
            'email_verified_at': self.email_verified_at if self.email_verified_at else None,
            'timezone': self.timezone,
            'language': self.language,
            'theme': self.theme,
        }

        if include_sensitive:
            user_dict.update({
                'failed_login_attempts': self.failed_login_attempts,
                'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
                'is_superuser': self.is_superuser,
            })

        return user_dict


    # # Example usage and database setup
    # if __name__ == "__main__":
    #     from sqlalchemy import create_engine
    #     from sqlalchemy.orm import sessionmaker
    #
    #     # Create database engine (using SQLite for example)
    #     engine = create_engine('sqlite:///users.db', echo=True)
    #
    #     # Create all tables
    #     Base.metadata.create_all(engine)
    #
    #     # Create session
    #     Session = sessionmaker(bind=engine)
    #     session = Session()
    #
    #     # Create a new user
    #     new_user = User(
    #         username='john_doe',
    #         email='john@example.com',
    #         password='secure_password123',
    #         first_name='John',
    #         last_name='Doe',
    #         phone_number='+1234567890'
    #     )
    #
    #     # Generate verification token
    #     verification_token = new_user.generate_verification_token()
    #     print(f"Verification token: {verification_token}")
    #
    #     # Add user to database
    #     session.add(new_user)
    #     session.commit()
    #
    #     print(f"Created user: {new_user}")
    #     print(f"User dict: {new_user.to_dict()}")
    #
    #     # Query user
    #     user = session.query(User).filter_by(username='john_doe').first()
    #     print(f"Found user: {user}")
    #
    #     # Test password
    #     print(f"Password check: {user.check_password('secure_password123')}")
    #
    #     session.close()
    #

