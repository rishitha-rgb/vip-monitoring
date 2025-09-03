import snscrape.modules.twitter as sntwitter
import yaml
from storage.canonical import CanonicalItem, DuckDBStorage

# Load config
with open("configs/sources.yaml") as f:
    config = yaml.safe_load(f)

storage = DuckDBStorage()

def scrape_twitter(query="OpenAI", limit=5):
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        item = CanonicalItem(
            text=tweet.content,
            author=tweet.user.username,
            source="twitter",
            metadata={"likes": tweet.likeCount, "retweets": tweet.retweetCount}
        )
        storage.insert_item(item)

if __name__ == "__main__":
    scrape_twitter()
