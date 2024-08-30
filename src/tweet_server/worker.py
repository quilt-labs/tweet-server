import os
import json
import tweepy
from rq import Worker, Queue, Connection
import redis


class TweepyClient:
    def __init__(self, key_path):
        with open(key_path) as f:
            x_secrets = json.load(f)

        self.consumer_key = x_secrets["api_key"]
        self.consumer_secret = x_secrets["api_secret"]
        self.access_token = x_secrets["access_token"]
        self.access_token_secret = x_secrets["access_secret"]

        self.client_v2 = tweepy.Client(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )

    def send_tweet(self, text):
        if len(text) > 278:
            raise ValueError(f"text `{text}` is too long ({len(text)} chars)")

        response = self.client_v2.create_tweet(text=text)
        return response


def send_tweet(tweet_data):
    container_key_path = os.environ.get("CONTAINER_KEY_PATH")
    tweepy_client = TweepyClient(container_key_path)

    text = tweet_data["text"]
    try:
        response = tweepy_client.send_tweet(text=text)
        return {"status": "completed", "response": str(response)}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def worker():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    redis_conn = redis.from_url(redis_url)

    with Connection(redis_conn):
        worker = Worker(Queue("tweets"))
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    worker()
