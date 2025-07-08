# Use official Python image
FROM python:3.10-slim
EXPOSE 8080

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-core.txt
RUN pip install --no-cache-dir uvloop httptools

# Expose application port


# Start the server
CMD ["python", "run_server.py"] 