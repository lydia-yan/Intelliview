# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy your code
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

# Set Python path so `from backend.xxx` works
ENV PYTHONPATH="/app"

# Expose port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Run FastAPI app with uvicorn
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]