# API Setup Guide

This guide will walk you through the process of obtaining the necessary API access tokens for the tweet-server.

## Twitter API Setup

1. Go to the Twitter Developer Portal (https://developer.twitter.com/en/portal/dashboard) and sign in with your Twitter account.

2. Create a new project and app in the developer portal.

3. In your app settings, navigate to the "Keys and Tokens" tab.

4. You will need the following credentials:
   - API Key (Consumer Key)
   - API Key Secret (Consumer Secret)
   - Access Token
   - Access Token Secret

5. Make sure your app has the necessary permissions to read and write tweets.

## Creating the Security Keys

1. In the root directory of the tweet-server project, create a folder named `security_keys`.

2. Inside the `security_keys` folder, create a file named `x.json` with the following content:

   ```json
   {
     "api_key": "your_twitter_api_key",
     "api_secret": "your_twitter_api_secret",
     "access_token": "your_twitter_access_token",
     "access_secret": "your_twitter_access_secret"
   }
   ```

   Replace the placeholder values with your actual Twitter API credentials.

3. In the same `security_keys` folder, create a file named `api_key.txt` containing a single line with your chosen API key for authenticating requests to the tweet-server. This can be any secure string you choose.

## Securing Your Credentials

Remember to keep your API credentials and keys secure:

- Never commit the `security_keys` folder to version control.
- Add `security_keys/` to your `.gitignore` file.
- Use environment variables or secure secret management systems in production environments.

With these steps completed, your tweet-server will be properly configured to use the Twitter API.
