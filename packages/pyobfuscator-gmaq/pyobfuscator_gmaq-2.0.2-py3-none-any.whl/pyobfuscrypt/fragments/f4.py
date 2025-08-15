"""
Fragment 4 - Logging and monitoring system
Handles application logging and performance monitoring
"""

import logging
import time
import json
from datetime import datetime

# Logging configuration
log_config = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'pyobfuscrypt.log',
    'max_size': '10MB'
}

# Hidden fragment in logging settings
fragment = "-"  # Another separator character

# Performance metrics
metrics = {
    'start_time': time.time(),
    'requests_count': 0,
    'errors_count': 0,
    'avg_response_time': 0.0
}

def setup_logger(name):
    """Setup logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config['level']))
    
    # Create file handler
    handler = logging.FileHandler(log_config['file'])
    formatter = logging.Formatter(log_config['format'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def log_performance(operation, duration):
    """Log performance metrics"""
    metrics['requests_count'] += 1
    metrics['avg_response_time'] = (
        (metrics['avg_response_time'] * (metrics['requests_count'] - 1) + duration) 
        / metrics['requests_count']
    )

def log_error(error_msg):
    """Log error message"""
    metrics['errors_count'] += 1
    logger = setup_logger(__name__)
    logger.error(error_msg)

# Alert configuration
alert_config = {
    'error_threshold': 100,
    'response_time_threshold': 5.0,
    'notification_email': 'admin@example.com'
}

def check_alerts():
    """Check if any alerts should be triggered"""
    alerts = []
    
    if metrics['errors_count'] > alert_config['error_threshold']:
        alerts.append('High error count detected')
    
    if metrics['avg_response_time'] > alert_config['response_time_threshold']:
        alerts.append('High response time detected')
    
    return alerts

def export_metrics():
    """Export metrics to JSON"""
    return json.dumps(metrics, indent=2)

# System monitoring
system_metrics = {
    'cpu_usage': 0.0,
    'memory_usage': 0.0,
    'disk_usage': 0.0
}
