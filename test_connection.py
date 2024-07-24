from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Database URI and SSL configuration
DATABASE_URI = ''
SSL_ARGS = {
    'sslmode': 'require',
    'sslrootcert': 'flask_invoice_app/ca/ca.pem'
}

# Create engine with SSL arguments
engine = create_engine(
    DATABASE_URI,
    connect_args=SSL_ARGS
)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except OperationalError as e:
    print(f"Connection failed: {e}")
