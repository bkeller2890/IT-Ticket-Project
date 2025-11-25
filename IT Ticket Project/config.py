import os

# NOTE: The default SECRET_KEY is only for development. For production set
# the SECRET_KEY environment variable to a secure random value.
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "tickets.db")
