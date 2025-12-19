# Use a slim Python image for smaller size
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# If using a local file like a SQLite DB, copy it here
# You should download Chinook.sqlite and place it in your project directory

# Copy your Vanna configuration file
COPY app.py .

# Expose the port (FastAPI default is 8000)
EXPOSE 8000

# Command to run the application using uvicorn
# The format is [ASGI_module]:[ASGI_app_variable_name]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
