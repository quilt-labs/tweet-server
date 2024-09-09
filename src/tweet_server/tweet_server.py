import uvicorn
import argparse
import tempfile
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
import redis
from rq import Queue
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

security = HTTPBearer()


# Global variables
api_key = None
redis_conn = None
tweet_queue = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tweepy_client, api_key, redis_conn, tweet_queue
    container_key_path = os.environ.get("CONTAINER_KEY_PATH")
    container_api_key_path = os.environ.get("CONTAINER_API_KEY_PATH")

    if not container_key_path:
        raise ValueError("CONTAINER_KEY_PATH environment variable is not set")
    if not container_api_key_path:
        raise ValueError("CONTAINER_API_KEY_PATH environment variable is not set")

    with open(container_api_key_path, "r") as f:
        api_key = f.read().strip()

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    redis_conn = redis.from_url(redis_url)
    tweet_queue = Queue("tweets", connection=redis_conn)

    yield


app = FastAPI(lifespan=lifespan)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return token


def enqueue_tweet(text: str, image_path: str | None, in_reply_to_tweet_id: str | None):
    tweet_data = {
        "text": text,
        "image_path": image_path,
        "in_reply_to_tweet_id": in_reply_to_tweet_id,
    }

    if tweet_queue is None:
        raise ValueError("tweet_queue is not initialized")

    job = tweet_queue.enqueue("tweet_server.worker.send_tweet", tweet_data)
    return job.id


@app.post("/tweet")
async def queue_tweet(
    text: str,
    in_reply_to_tweet_id: str | None = None,
    token: str = Depends(verify_token),
):
    job_id = enqueue_tweet(
        text=text, image_path=None, in_reply_to_tweet_id=in_reply_to_tweet_id
    )
    return {"status": "queued", "job_id": job_id}


@app.post("/tweet_with_image")
async def queue_tweet_with_image(
    text: str,
    in_reply_to_tweet_id: str | None = None,
    image: UploadFile = File(...),
    token: str = Depends(verify_token),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
        temp_image.write(await image.read())
        temp_image_path = temp_image.name

    job_id = enqueue_tweet(
        text=text, image_path=temp_image_path, in_reply_to_tweet_id=in_reply_to_tweet_id
    )
    return {"status": "queued", "job_id": job_id}


def main():
    parser = argparse.ArgumentParser(description="Run the tweet server")
    parser.add_argument(
        "--port",
        type=int,
        default=6900,
        help="Port to run the server on (default: 6900)",
    )
    args = parser.parse_args()

    uvicorn.run(
        "tweet_server.tweet_server:app", host="0.0.0.0", port=args.port, reload=True
    )


if __name__ == "__main__":
    main()
