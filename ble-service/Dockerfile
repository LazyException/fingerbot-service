FROM python:3.11-slim

# Install BlueZ and Bluetooth dependencies
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port 4000
EXPOSE 4000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000"]
