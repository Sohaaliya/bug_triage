# Use a lightweight official Python runtime as a base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to utilize Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and static files
COPY src/ ./src/

# Copy the trained machine learning models and encoders
COPY models/ ./models/

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Start the application using Uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]