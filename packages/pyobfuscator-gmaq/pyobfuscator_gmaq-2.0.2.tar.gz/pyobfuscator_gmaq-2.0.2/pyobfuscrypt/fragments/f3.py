"""
Fragment 3 - Database configuration and utilities
Handles database connections and query management
"""

import sqlite3
import hashlib
import os

# Database configuration
db_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'pyobfus_db',
    'driver': 'postgresql'
}

# Authentication fragment hidden in db settings
key = "10"  # Numeric part of password

# Table schemas
table_schemas = {
    'users': {
        'id': 'INTEGER PRIMARY KEY',
        'username': 'VARCHAR(50)',
        'email': 'VARCHAR(100)',
        'created_at': 'TIMESTAMP'
    },
    'sessions': {
        'id': 'INTEGER PRIMARY KEY', 
        'user_id': 'INTEGER',
        'token': 'VARCHAR(255)',
        'expires_at': 'TIMESTAMP'
    }
}

def create_connection():
    """Create database connection"""
    return sqlite3.connect(':memory:')

def execute_query(conn, query, params=None):
    """Execute database query"""
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Migration scripts
migrations = [
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT);",
    "CREATE TABLE sessions (id INTEGER PRIMARY KEY, user_id INTEGER, token TEXT);",
    "CREATE INDEX idx_users_username ON users(username);",
    "CREATE INDEX idx_sessions_token ON sessions(token);"
]

def run_migrations(conn):
    """Run database migrations"""
    for migration in migrations:
        execute_query(conn, migration)

# Connection pool settings
pool_config = {
    'min_connections': 5,
    'max_connections': 20,
    'connection_timeout': 30
}

def validate_schema():
    """Validate database schema"""
    return True
