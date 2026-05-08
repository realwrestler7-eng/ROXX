"""
ROXX AI - Application Factory & CLI Commands
Part 1 (Final): Flask app initialization and utility functions

This module provides:
- Application factory pattern
- CLI commands for database management
- Error handlers
- Request logging
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from datetime import datetime
from models import db, User, seed_database
from config import get_config

# Configure logging
def setup_logging(app):
    """
    Configure logging for the application
    
    Args:
        app: Flask application instance
    """
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/roxx_ai.log',
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)


def create_app(config_name=None):
    """
    Application factory function
    
    Creates and configures Flask application
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application
    """
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app)
    app.logger.info(f"🚀 Starting ROXX AI in {config_name} mode")
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Request/Response logging
    @app.before_request
    def log_request():
        """Log incoming requests"""
        g.start_time = datetime.utcnow()
        app.logger.debug(f"→ {request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses"""
        if hasattr(g, 'start_time'):
            elapsed = (datetime.utcnow() - g.start_time).total_seconds()
            app.logger.debug(f"← {response.status_code} ({elapsed:.2f}s)")
        return response
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Database initialization
    with app.app_context():
        db.create_all()
        app.logger.info("✅ Database tables created")
    
    app.logger.info("🎉 ROXX AI Application initialized!")
    
    return app


def register_error_handlers(app):
    """
    Register error handlers for different HTTP status codes
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request"""
        app.logger.warning(f"Bad request: {error}")
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized"""
        app.logger.warning(f"Unauthorized access attempt")
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Please login first'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden"""
        app.logger.warning(f"Forbidden access: {error}")
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found"""
        app.logger.debug(f"Resource not found: {request.path}")
        return jsonify({
            'success': False,
            'error': 'Not found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f"Internal server error: {error}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'Something went wrong on our end'
        }), 500


def register_cli_commands(app):
    """
    Register Flask CLI commands
    
    Args:
        app: Flask application instance
    """
    
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        db.create_all()
        print("✅ Database initialized!")
    
    @app.cli.command('drop-db')
    def drop_db_command():
        """Drop all database tables."""
        confirmation = input("⚠️ Are you sure? This will delete all data. (yes/no): ")
        if confirmation.lower() == 'yes':
            db.drop_all()
            print("🗑️ Database dropped!")
        else:
            print("❌ Operation cancelled")
    
    @app.cli.command('seed-db')
    def seed_db_command():
        """Seed database with test data."""
        seed_database()
        print("🌱 Database seeded with test data!")
    
    @app.cli.command('create-admin')
    def create_admin_command():
        """Create an admin user."""
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password (min 6 chars): ")
        
        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            return
        
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print("❌ User already exists!")
            return
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name="Admin User",
            is_active=True,
            is_verified=True,
            subscription_type='pro',
            ai_credits=10000
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        print(f"✅ Admin user '{username}' created successfully!")
    
    @app.cli.command('list-users')
    def list_users_command():
        """List all users in database."""
        users = User.query.all()
        if not users:
            print("No users found")
            return
        
        print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Credits':<10} {'Sub Type':<10}")
        print("="*75)
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.ai_credits:<10} {user.subscription_type:<10}")
    
    @app.cli.command('reset-credits')
    def reset_credits_command():
        """Reset all user credits."""
        confirmation = input("⚠️ Reset all users' credits to 100? (yes/no): ")
        if confirmation.lower() == 'yes':
            users = User.query.all()
            for user in users:
                user.ai_credits = 100
            db.session.commit()
            print(f"✅ Reset credits for {len(users)} users!")
        else:
            print("❌ Operation cancelled")


# Initialize app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
