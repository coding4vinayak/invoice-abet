from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Database URI and SSL configuration
DATABASE_URI = 'postgresql+psycopg2://avnadmin:AVNS_Ao36hgoqP-xU5EiyEsn@pg-17ae6fae-vinayakdb.a.aivencloud.com:28101/defaultdb'
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
