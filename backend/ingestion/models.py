# src/models.py
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid
import json

@dataclass
class CanonicalItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = None             # e.g., 'twitter','reddit','github','telegram'
    platform_id: str = None          # original post id
    vip_target: str = None           # which VIP this mentions (optional)
    author: str = None
    author_id: str = None
    text: str = ''
    created_at: datetime = None
    url: str = None
    metadata: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)
    ingested_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'platform_id': self.platform_id,
            'vip_target': self.vip_target,
            'author': self.author,
            'author_id': self.author_id,
            'text': self.text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'url': self.url,
            'metadata': json.dumps(self.metadata, default=str),
            'raw': json.dumps(self.raw, default=str),
            'ingested_at': self.ingested_at.isoformat() if self.ingested_at else None
        }
