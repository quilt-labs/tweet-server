# Use a slim Python image
FROM python:3.12-slim

# Install Redis, procps, and other required system dependencies
RUN apt-get update && apt-get install -y redis-server procps

# Set working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml poetry.lock* /app/
COPY src /app/src
COPY security_keys/x.json /app/keys/
COPY security_keys/api_key.txt /app/keys/
COPY README.md /app/

# Install Poetry and project dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Install the tweet-server package
RUN pip install -e .

# Expose port 6900 for the FastAPI app (new default port)
EXPOSE 6900

# Set environment variables for the key file, API key, and Redis URL inside the container
ENV CONTAINER_KEY_PATH=/app/keys/x.json
ENV CONTAINER_API_KEY_PATH=/app/keys/api_key.txt
ENV REDIS_URL=redis://localhost:6379

# Create a script to run Redis, the server, and the worker
RUN echo '#!/bin/sh\n\
trap "exit" INT TERM\n\
trap "kill 0" EXIT\n\
redis-server --daemonize yes\n\
python -m tweet_server --port 6900 &\n\
python -m tweet_server.worker &\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/bin/sh", "-c", "/app/start.sh"]