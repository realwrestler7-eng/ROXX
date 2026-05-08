"""
ROXX AI - Database Configuration
Part 1: Database Setup & User Model

This module handles all database operations including:
- SQLAlchemy configuration
- User model with authentication
- Database initialization
- Migration support
"""

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """
    User Model - Stores all user information
    
    Attributes:
        id: Unique user identifier (Primary Key)
        username: Unique username for login
        email: User's email address
        password_hash: Hashed password for security
        full_name: User's full name
        avatar_url: Profile picture URL
        bio: User biography
        voice_preference: Boy/Girl voice preference
        theme: Light/Dark theme preference
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        is_active: Account status
        is_verified: Email verification status
        subscription_type: Free/Premium/Pro
        ai_credits: Credits for AI features
        preferences: JSON object for additional settings
    """
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    
    # Profile
    avatar_url = db.Column(db.String(255), nullable=True, default=None)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Preferences
    voice_preference = db.Column(
        db.String(10), 
        nullable=False, 
        default='boy',
        index=True
    )  # 'boy' or 'girl'
    theme = db.Column(
        db.String(10), 
        nullable=False, 
        default='light'
    )  # 'light' or 'dark'
    
    # Account Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    
    # Subscription
    subscription_type = db.Column(
        db.String(20), 
        nullable=False, 
        default='free'
    )  # 'free', 'premium', 'pro'
    ai_credits = db.Column(db.Integer, nullable=False, default=100)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Additional Settings
    preferences = db.Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_generations = db.relationship('AIGeneration', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """
        Hash and set password
        
        Args:
            password (str): Plain text password
        """
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """
        Verify password against hash
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        Convert user object to dictionary
        
        Returns:
            dict: User data as dictionary
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'voice_preference': self.voice_preference,
            'theme': self.theme,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'subscription_type': self.subscription_type,
            'ai_credits': self.ai_credits,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def add_credits(self, amount):
        """
        Add AI credits to user account
        
        Args:
            amount (int): Number of credits to add
        """
        if amount <= 0:
            raise ValueError("Credits amount must be positive")
        self.ai_credits += amount
        self.updated_at = datetime.utcnow()
    
    def deduct_credits(self, amount):
        """
        Deduct AI credits from user account
        
        Args:
            amount (int): Number of credits to deduct
            
        Returns:
            bool: True if deduction successful, False if insufficient credits
        """
        if amount <= 0:
            raise ValueError("Credits amount must be positive")
        if self.ai_credits < amount:
            return False
        self.ai_credits -= amount
        self.updated_at = datetime.utcnow()
        return True
    
    def upgrade_subscription(self, subscription_type, expiry_date):
        """
        Upgrade user subscription
        
        Args:
            subscription_type (str): 'premium' or 'pro'
            expiry_date (datetime): Subscription expiry date
        """
        if subscription_type not in ['free', 'premium', 'pro']:
            raise ValueError("Invalid subscription type")
        self.subscription_type = subscription_type
        self.subscription_expires_at = expiry_date
        
        # Give credits based on subscription
        if subscription_type == 'premium':
            self.ai_credits = 500
        elif subscription_type == 'pro':
            self.ai_credits = 2000
        
        self.updated_at = datetime.utcnow()


class Conversation(db.Model):
    """
    Conversation Model - Stores chat conversations
    
    Attributes:
        id: Unique conversation identifier
        user_id: Foreign key to User
        title: Conversation title
        messages: JSON array of messages
        created_at: Conversation creation timestamp
        updated_at: Last message timestamp
        is_archived: Archive status
    """
    
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=True)
    messages = db.Column(JSON, nullable=False, default=[])
    
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.id} - User {self.user_id}>'
    
    def add_message(self, sender, content, message_type='text'):
        """
        Add message to conversation
        
        Args:
            sender (str): 'user' or 'ai'
            content (str): Message content
            message_type (str): Type of message ('text', 'image', 'video', etc.)
        """
        message = {
            'id': len(self.messages) + 1,
            'sender': sender,
            'content': content,
            'type': message_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        if self.messages is None:
            self.messages = []
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': self.messages,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AIGeneration(db.Model):
    """
    AI Generation Model - Stores all AI-generated content
    
    Attributes:
        id: Unique generation identifier
        user_id: Foreign key to User
        generation_type: Type of generation (image, photo_repair, video, voice, etc.)
        prompt: Original prompt/input
        output_url: URL of generated content
        metadata: Additional generation data
        credits_used: Credits consumed
        status: Processing status
        created_at: Generation timestamp
    """
    
    __tablename__ = 'ai_generations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    generation_type = db.Column(
        db.String(50), 
        nullable=False,
        index=True
    )  # 'image', 'photo_repair', 'video', 'voice', 'singer', etc.
    
    prompt = db.Column(db.Text, nullable=False)
    output_url = db.Column(db.String(500), nullable=True)
    
    metadata = db.Column(JSON, nullable=True, default={})
    
    credits_used = db.Column(db.Integer, nullable=False, default=0)
    
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending',
        index=True
    )  # 'pending', 'processing', 'completed', 'failed'
    
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<AIGeneration {self.id} - {self.generation_type}>'
    
    def mark_completed(self, output_url):
        """
        Mark generation as completed
        
        Args:
            output_url (str): URL of generated content
        """
        self.status = 'completed'
        self.output_url = output_url
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error_message):
        """
        Mark generation as failed
        
        Args:
            error_message (str): Error description
        """
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'generation_type': self.generation_type,
            'prompt': self.prompt,
            'output_url': self.output_url,
            'status': self.status,
            'credits_used': self.credits_used,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class APIKey(db.Model):
    """
    API Key Model - Manages third-party API keys securely
    
    Attributes:
        id: Unique key identifier
        user_id: Owner of the API key
        service_name: Name of the service (openai, replicate, etc.)
        key_hash: Hashed API key
        is_active: Key status
        created_at: Creation timestamp
    """
    
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    service_name = db.Column(db.String(50), nullable=False)  # 'openai', 'replicate', 'huggingface', etc.
    key_hash = db.Column(db.String(255), nullable=False)
    
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIKey {self.service_name}>'


class UsageLog(db.Model):
    """
    Usage Log Model - Track user activities for analytics
    
    Attributes:
        id: Unique log identifier
        user_id: User who performed action
        action_type: Type of action
        details: Additional details
        timestamp: When action occurred
    """
    
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    action_type = db.Column(db.String(50), nullable=False, index=True)
    details = db.Column(JSON, nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<UsageLog {self.action_type}>'


# Database Initialization Function
def init_db(app):
    """
    Initialize database with Flask app
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database initialized successfully!")


def seed_database():
    """
    Seed database with test data (for development only)
    """
    # Check if test user already exists
    test_user = User.query.filter_by(username='testuser').first()
    
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@roxx.com',
            full_name='Test User',
            voice_preference='boy',
            theme='light',
            is_active=True,
            is_verified=True,
            subscription_type='free',
            ai_credits=100
        )
        test_user.set_password('testpass123')
        
        db.session.add(test_user)
        db.session.commit()
        print("✅ Test user created!")
    else:
        print("ℹ️ Test user already exists!")
