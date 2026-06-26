from database import Base, engine
import models  # Import your models to ensure they are registered with SQLAlchemy

def initialize_database():
    # Create all tables in the database
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()