import yaml
import snscrape.modules.twitter as sntwitter
from storage.canonical import CanonicalItem, DuckDBStorage

# Load config
with open("configs/sources.yaml") as f:
    config = yaml.safe_load(f)

storage = DuckDBStorage("vip_data.duckdb")

def scrape_twitter(query, limit=5):
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
    scrape_twitter("OpenAI")
