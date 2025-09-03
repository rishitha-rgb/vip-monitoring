"""
VIP Threat Monitoring - Data Ingestion Module
Collects posts from Twitter/X, Reddit, GitHub, and Telegram
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import duckdb
import pandas as pd
from dotenv import load_dotenv

# Social media scraping libraries
try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_AVAILABLE = True
except ImportError:
    SNSCRAPE_AVAILABLE = False

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    from telethon import TelegramClient
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_PATH', './data/vip_threats.db')
        self.vip_keywords = [k.strip() for k in os.getenv('VIP_KEYWORDS', '').split(',') if k.strip()]
        self.threat_keywords = [k.strip() for k in os.getenv('THREAT_KEYWORDS', '').split(',') if k.strip()]
        self._init_database()

    def _init_database(self):
        """Create DuckDB tables if not exists."""
        try:
            conn = duckdb.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id VARCHAR PRIMARY KEY,
                    platform VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    author_username VARCHAR,
                    author_id VARCHAR,
                    timestamp TIMESTAMP,
                    url VARCHAR,
                    likes INTEGER,
                    shares INTEGER,
                    comments INTEGER,
                    hashtags VARCHAR,
                    mentions VARCHAR,
                    metadata VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    threat_score DOUBLE DEFAULT 0.0,
                    threat_category VARCHAR DEFAULT 'unknown'
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts(timestamp);")
            conn.close()
            logger.info(f"DuckDB database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def scrape_twitter(self, max_posts: int = 200) -> List[Dict[str, Any]]:
        """Scrape Twitter posts using snscrape."""
        posts = []
        if not SNSCRAPE_AVAILABLE:
            logger.warning("snscrape not installed, skipping Twitter ingestion.")
            return posts
        try:
            vip_query = " OR ".join(f'"{kw}"' for kw in self.vip_keywords[:5])
            since_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
            query = f"({vip_query}) since:{since_date}"
            scraper = sntwitter.TwitterSearchScraper(query)
            count = 0
            for tweet in scraper.get_items():
                if count >= max_posts:
                    break
                post = {
                    'id': f"twitter_{tweet.id}",
                    'platform': 'twitter',
                    'content': tweet.content,
                    'author_username': tweet.user.username if tweet.user else None,
                    'author_id': str(tweet.user.id) if tweet.user else None,
                    'timestamp': tweet.date,
                    'url': tweet.url,
                    'likes': getattr(tweet, 'likeCount', 0),
                    'shares': getattr(tweet, 'retweetCount', 0),
                    'comments': getattr(tweet, 'replyCount', 0),
                    'hashtags': json.dumps(tweet.hashtags or []),
                    'mentions': json.dumps([user.username for user in (tweet.mentionedUsers or [])]),
                    'metadata': json.dumps({
                        'lang': getattr(tweet, 'lang', None),
                        'verified': getattr(tweet.user, 'verified', False),
                        'followers_count': getattr(tweet.user, 'followersCount', 0)
                    }),
                }
                posts.append(post)
                count += 1
            logger.info(f"Scraped {len(posts)} tweets matching VIP keywords.")
        except Exception as e:
            logger.error(f"Error scraping Twitter: {e}")
        return posts

    def scrape_reddit(self, max_posts: int = 150) -> List[Dict[str, Any]]:
        """Scrape Reddit posts using PRAW."""
        posts = []
        if not PRAW_AVAILABLE:
            logger.warning("PRAW not installed, skipping Reddit ingestion.")
            return posts
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'VIPThreatMonitor/1.0')
            )
            subreddits = ['all', 'politics', 'news', 'worldnews', 'celebrities']
            posts_per_sub = max_posts // len(subreddits)
            for sub in subreddits:
                subreddit = reddit.subreddit(sub)
                query = " OR ".join(self.vip_keywords[:3])
                for submission in subreddit.search(query, sort='new', time_filter='week', limit=posts_per_sub):
                    content = submission.title
                    if submission.selftext:
                        content += f"\n\n{submission.selftext}"
                    post = {
                        'id': f"reddit_{submission.id}",
                        'platform': 'reddit',
                        'content': content,
                        'author_username': str(submission.author) if submission.author else '[deleted]',
                        'author_id': str(submission.author.id) if submission.author else 'deleted',
                        'timestamp': datetime.utcfromtimestamp(submission.created_utc),
                        'url': f"https://reddit.com{submission.permalink}",
                        'likes': submission.score,
                        'shares': 0,
                        'comments': submission.num_comments,
                        'hashtags': json.dumps([]),
                        'mentions': json.dumps([]),
                        'metadata': json.dumps({
                            'subreddit': str(submission.subreddit),
                            'flair': submission.link_flair_text,
                            'gilded': submission.gilded,
                            'nsfw': submission.over_18,
                        }),
                    }
                    posts.append(post)
            logger.info(f"Scraped {len(posts)} Reddit posts matching VIP keywords.")
        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
        return posts

    def scrape_github(self, max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape GitHub issues with PyGithub."""
        posts = []
        if not GITHUB_AVAILABLE:
            logger.warning("PyGithub not installed, skipping GitHub ingestion.")
            return posts
        try:
            token = os.getenv('GITHUB_TOKEN')
            gh = Github(token) if token else Github()
            query = " ".join(f'"{kw}"' for kw in self.vip_keywords[:3])
            query += " type:issue created:>2024-01-01"
            issues = gh.search_issues(query, sort='created', order='desc')
            count = 0
            for issue in issues:
                if count >= max_posts:
                    break
                content = issue.title
                if issue.body:
                    content += f"\n\n{issue.body}"
                post = {
                    'id': f"github_{issue.id}",
                    'platform': 'github',
                    'content': content,
                    'author_username': issue.user.login if issue.user else None,
                    'author_id': str(issue.user.id) if issue.user else None,
                    'timestamp': issue.created_at,
                    'url': issue.html_url,
                    'likes': 0,
                    'shares': 0,
                    'comments': issue.comments,
                    'hashtags': json.dumps([]),
                    'mentions': json.dumps([]),
                    'metadata': json.dumps({
                        'repo': issue.repository.full_name if issue.repository else None,
                        'state': issue.state,
                        'labels': [label.name for label in issue.labels],
                    }),
                }
                posts.append(post)
                count += 1
            logger.info(f"Scraped {len(posts)} GitHub issues matching VIP keywords.")
        except Exception as e:
            logger.error(f"Error scraping GitHub: {e}")
        return posts

    def scrape_telegram(self, max_posts: int = 50) -> List[Dict[str, Any]]:
        """Scrape Telegram via Telethon - requires phone login manually."""
        posts = []
        if not TELETHON_AVAILABLE:
            logger.warning("Telethon not installed, skipping Telegram ingestion.")
            return posts

        logger.warning("Telegram scraping requires manual setup and phone authentication. Skipping by default.")
        return posts

    def store_posts(self, posts: List[Dict[str, Any]]) -> int:
        """Store unique posts into DuckDB."""
        if not posts:
            return 0
        try:
            conn = duckdb.connect(self.db_path)
            stored = 0
            for post in posts:
                exists = conn.execute("SELECT 1 FROM posts WHERE id = ?", (post['id'],)).fetchone()
                if exists:
                    continue
                conn.execute("""
                    INSERT INTO posts (
                        id, platform, content, author_username, author_id,
                        timestamp, url, likes, shares, comments,
                        hashtags, mentions, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post['id'], post['platform'], post['content'], post['author_username'],
                    post['author_id'], post['timestamp'], post['url'], post['likes'],
                    post['shares'], post['comments'], post['hashtags'], post['mentions'],
                    post['metadata'], datetime.utcnow()
                ))
                stored += 1
            conn.close()
            logger.info(f"Stored {stored} new posts.")
            return stored
        except Exception as e:
            logger.error(f"Failed to store posts: {e}")
            return 0

    def run_ingestion_cycle(self) -> Dict[str, Any]:
        logger.info("Starting ingestion cycle")
        results = {
            'platforms': {},
            'total_collected': 0,
            'total_stored': 0
        }

        sources = [
            ('twitter', self.scrape_twitter, 200),
            ('reddit', self.scrape_reddit, 150),
            ('github', self.scrape_github, 100),
            ('telegram', self.scrape_telegram, 50),
        ]

        all_posts = []
        for name, func, limit in sources:
            try:
                posts = func(limit)
                all_posts.extend(posts)
                results['platforms'][name] = len(posts)
            except Exception as e:
                logger.error(f"Error scraping {name}: {e}")
                results['platforms'][name] = 0

        results['total_collected'] = len(all_posts)
        results['total_stored'] = self.store_posts(all_posts)

        logger.info(f"Ingestion cycle completed: {results['total_stored']} posts stored from {results['total_collected']} collected")
        return results

    def _get_db_connection(self):
        return duckdb.connect(self.db_path)

    def get_posts_for_analysis(self, limit: int = 1000) -> pd.DataFrame:
        try:
            conn = self._get_db_connection()
            df = conn.execute("""
                SELECT * FROM posts
                WHERE threat_score = 0.0 OR threat_category = 'unknown'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,)).df()
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Failed to load posts for analysis: {e}")
            return pd.DataFrame()

    def update_post_scores(self, post_scores: List[Dict[str, Any]]) -> int:
        if not post_scores:
            return 0
        try:
            conn = self._get_db_connection()
            updated = 0
            for score in post_scores:
                conn.execute("""
                    UPDATE posts
                    SET threat_score = ?, threat_category = ?
                    WHERE id = ?
                """, (score['threat_score'], score['threat_category'], score['post_id']))
                updated += 1
            conn.close()
            logger.info(f"Updated threat scores for {updated} posts.")
            return updated
        except Exception as e:
            logger.error(f"Failed to update post scores: {e}")
            return 0


if __name__ == "__main__":
    ingestion = DataIngestion()
    results = ingestion.run_ingestion_cycle()
    print(f"Collected: {results['total_collected']} posts")
    print(f"Stored: {results['total_stored']} posts")
