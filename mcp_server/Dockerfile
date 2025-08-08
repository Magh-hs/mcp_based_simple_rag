FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY server.py .
COPY resources/ ./resources/
COPY prompts/ ./prompts/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (if needed for HTTP interface)
EXPOSE 8001

# Run the MCP server
CMD ["python", "server.py"]