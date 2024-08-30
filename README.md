# tweet-server

A server for queuing and sending tweets using FastAPI, Redis, and Tweepy.

## Setup

### 1. Security Keys

Before building the Docker image, you need to set up the `security_keys` folder with the necessary credentials:

1. Create a folder named `security_keys` in the root directory of the project.
2. Inside the `security_keys` folder, create two files:
   1. `x.json`: This file should contain your Twitter API credentials in JSON format:
   ```json
   {
     "api_key": "your_api_key",
     "api_secret": "your_api_secret",
     "access_token": "your_access_token",
     "access_secret": "your_access_secret"
   }
   ```
   2. `api_key.txt`: This file should contain a single line with your chosen API key for authenticating requests to the tweet-server.

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
