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

        self.client_v1 = self.get_twitter_conn_v1(
            api_key=self.consumer_key,
            api_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )

    def get_twitter_conn_v1(
        self, api_key, api_secret, access_token, access_token_secret
    ) -> tweepy.API:
        """Get twitter conn 1.1"""

        auth = tweepy.OAuth1UserHandler(
            consumer_key=api_key, consumer_secret=api_secret
        )
        auth.set_access_token(
            key=access_token,
            secret=access_token_secret,
        )
        return tweepy.API(auth)

    def send_tweet(
        self,
        text,
        image_path: str | None = None,
        in_reply_to_tweet_id: str | None = None,
    ):
        if len(text) > 278:
            raise ValueError(f"text `{text}` is too long ({len(text)} chars)")

        if image_path is None:
            if in_reply_to_tweet_id is None:
                response = self.client_v2.create_tweet(text=text)
            else:
                response = self.client_v2.create_tweet(
                    text=text, in_reply_to_tweet_id=in_reply_to_tweet_id
                )
            return response

        # upload media
        ## make sure image_path is .png or .jpg
        if not (image_path.endswith("png") or image_path.endswith("jpg")):
            raise ValueError("image must be a png or jpg")

        media = self.client_v1.media_upload(filename=image_path)
        if media is None:
            raise ValueError("media upload failed")
        media_id = media.media_id

        response = self.client_v2.create_tweet(
            text=text, media_ids=[media_id], in_reply_to_tweet_id=in_reply_to_tweet_id
        )
        return response


def send_tweet(tweet_data):
    container_key_path = os.environ.get("CONTAINER_KEY_PATH")
    tweepy_client = TweepyClient(container_key_path)

    text = tweet_data["text"]
    image_path = tweet_data.get("image_path")
    in_reply_to_tweet_id = tweet_data.get("in_reply_to_tweet_id")

    try:
        response = tweepy_client.send_tweet(
            text=text, image_path=image_path, in_reply_to_tweet_id=in_reply_to_tweet_id
        )

        if image_path:
            os.unlink(image_path)

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
