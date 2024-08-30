# tweet-server

A server for queuing and sending tweets using FastAPI, Redis, and Tweepy.

## Setup

### 1. Security Keys

Before building the Docker image, you need to set up the `security_keys` folder with the necessary credentials:

1. Follow the detailed instructions in the [API Setup Guide](docs/api_setup_guide.md) to obtain your Twitter API credentials and create the required files.

2. Make sure you have created the `security_keys` folder in the root directory of the project with the following files:
   - `x.json`: Contains your Twitter API credentials
   - `api_key.txt`: Contains your chosen API key for authenticating requests to the tweet-server

For security reasons, never commit the `security_keys` folder to version control.

### 2. Building and Running the Docker Image

1. Make sure you have Docker installed on your system.
2. Open a terminal and navigate to the root directory of the project.
3. Build the Docker image:
   ```
   docker build -t tweet-server .
   ```
4. Run the Docker container:
   ```
   docker run -p 6900:6900 tweet-server
   ```

The server will now be running and accessible at `http://localhost:6900`.

## Usage

To queue a tweet, send a POST request to the `/tweet` endpoint with the following:

- Header: `Authorization: Bearer your_api_key` (use the key from `api_key.txt`)
- Body: JSON object with a `text` field containing the tweet content

Example using curl:

```bash
curl -X POST http://localhost:6900/tweet \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_api_key" \
-d '{"text": "Hello, world! This is a test tweet from tweet-server."}'
```