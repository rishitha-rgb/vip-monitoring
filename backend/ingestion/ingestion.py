# ingestion.py

import snscrape.modules.twitter as sntwitter
import praw
from github import Github
from telethon import TelegramClient, events, sync
import asyncio

class DataIngestion:
    def __init__(self, twitter_username, reddit_client_id, reddit_client_secret, reddit_user_agent,
                 github_access_token, telegram_api_id, telegram_api_hash, telegram_username):
        # Initialize Twitter scraper username
        self.twitter_username = twitter_username

        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )

        # Initialize Github client
        self.g = Github(github_access_token)

        # Initialize Telegram client
        self.telegram_client = TelegramClient('session_name', telegram_api_id, telegram_api_hash)
        self.telegram_username = telegram_username

    def scrape_twitter(self, limit=100):
        tweets = []
        for i, tweet in enumerate(sntwitter.TwitterUserScraper(self.twitter_username).get_items()):
            if i >= limit:
                break
            tweets.append({
                "id": tweet.id,
                "content": tweet.content,
                "date": tweet.date,
                "url": tweet.url
            })
        return tweets

    def scrape_reddit(self, subreddit_name, limit=100):
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=limit):
            posts.append({
                "id": post.id,
                "title": post.title,
                "selftext": post.selftext,
                "url": post.url,
                "created_utc": post.created_utc
            })
        return posts

    def scrape_github(self, repo_name, limit=100):
        repo = self.g.get_repo(repo_name)
        issues = repo.get_issues(state='open')
        collected = []
        for i, issue in enumerate(issues):
            if i >= limit:
                break
            collected.append({
                "id": issue.id,
                "title": issue.title,
                "body": issue.body,
                "url": issue.html_url,
                "created_at": issue.created_at
            })
        return collected

    async def scrape_telegram(self, channel_username, limit=100):
        await self.telegram_client.start()
        posts = []
        async for message in self.telegram_client.iter_messages(channel_username, limit=limit):
            posts.append({
                "id": message.id,
                "text": message.message,
                "date": message.date,
                "url": f"https://t.me/{channel_username}/{message.id}"
            })
        return posts

# Usage example (needs proper credentials):
# ingestion = DataIngestion(twitter_username='user', reddit_client_id='id', reddit_client_secret='secret',
#                           reddit_user_agent='agent', github_access_token='token',
#                           telegram_api_id=12345, telegram_api_hash='hash', telegram_username='username')
# twitter_posts = ingestion.scrape_twitter()
