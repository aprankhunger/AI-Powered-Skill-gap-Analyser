from dotenv import load_dotenv
import os

# Load environment variables first, before initializing anything else
load_dotenv()

from app import create_app
from app.models import db

app = create_app()

# Ensure database tables are created
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
