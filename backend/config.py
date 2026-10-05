import os

class Config:
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database configuration
    # Get the absolute path to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(backend_dir, 'database', 'network_data.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT Configuration
    MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Router monitoring
    ROUTER_SCAN_INTERVAL = int(os.environ.get('ROUTER_SCAN_INTERVAL', 10))

# Create config instance
config = Config()