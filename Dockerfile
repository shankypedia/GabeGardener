FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create config directory
RUN mkdir -p /root/.gabegardener

# Expose dashboard port
EXPOSE 5000

# Set environment variables
ENV GABEGARDENER_DASHBOARD=true
ENV GABEGARDENER_DASHBOARD_PORT=5000

# Run the application
CMD ["python", "main.py"]
