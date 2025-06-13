import psycopg2
from sqlalchemy import create_engine

def connect_to_database():
    # connect to postgres database using SQLAlchemy
    try:
        # Create SQLAlchemy engine for PostgreSQL
        engine = create_engine(f"postgresql://zacharyplischka@localhost/afl_database")
        # Test the connection
        with engine.connect() as conn:
            pass
        print("✅ Database connection established")
        return engine
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def connect_to_database_raw():
    # connect to postgres database using raw psycopg2 (for non-pandas operations)
    try:
        conn = psycopg2.connect(f"dbname='afl_database' user='zacharyplischka' host='localhost'")
        print("✅ Raw database connection established")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None
    
