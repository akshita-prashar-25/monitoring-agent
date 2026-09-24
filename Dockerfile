FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy monitoring agent
COPY agent.py .

# Backend address will be provided by Docker Compose
ENV BACKEND_URL=http://backend:8080

# Start the monitoring agent
CMD ["python", "agent.py"]