from src.models import CanonicalItem, insert_item

def seed_mock_data():
    items = [
        CanonicalItem(
            source="twitter",
            vip_name="Elon Musk",
            vip_type="person",
            content="This is a mock tweet",
            url="https://twitter.com/elonmusk/status/1",
            timestamp="2025-09-03T12:00:00"
        ),
        CanonicalItem(
            source="reddit",
            vip_name="NASA",
            vip_type="organization",
            content="This is a mock Reddit post",
            url="https://reddit.com/r/nasa/1",
            timestamp="2025-09-03T13:00:00"
        )
    ]
    for item in items:
        insert_item(item)
        print(f"Inserted mock item for {item.vip_name}")

if __name__ == "__main__":
    seed_mock_data()
