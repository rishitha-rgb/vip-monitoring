"""
VIP Threat Monitoring - AI Scoring Module
Machine Learning model for threat detection and scoring
"""

import os
import json
import logging
import re
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VIPThreatScorer:
    def __init__(self):
        self.model_path = os.getenv('MODEL_PATH', './models/vip_threat_model.pkl')
        self.threat_threshold = float(os.getenv('THREAT_THRESHOLD', 0.7))
        self.vip_keywords = [k.strip() for k in os.getenv('VIP_KEYWORDS', '').split(',') if k.strip()]
        self.threat_keywords = [k.strip() for k in os.getenv('THREAT_KEYWORDS', '').split(',') if k.strip()]

        self.pipeline = None  # Will hold the trained pipeline
        self.categories = {
            0: 'safe',
            1: 'harassment',
            2: 'threat',
            3: 'doxxing',
            4: 'misinformation',
            5: 'spam'
        }

        # Load existing model if available
        self._load_model()

    def create_training_data(self):
        # Synthetic training data samples to simulate real threat categories
        data = []

        threat_samples = [
            "This politician should be eliminated permanently",
            "Someone needs to take out this corrupt leader",
            "The president deserves to die for what they've done",
            "I'm going to hunt down this celebrity",
            "Time to bomb the senator's office",
            "This minister should be shot in the head",
            "Going to assassinate this corrupt official",
            "The mayor needs to be destroyed completely"
        ]
        harassment_samples = [
            "This celebrity is absolutely disgusting and worthless",
            "The politician is a complete idiot and moron",
            "This leader is trash and should disappear",
            "I hate this minister more than anything",
            "The senator is the worst human being alive",
            "This official makes me sick to my stomach"
        ]
        doxxing_samples = [
            "Found the home address of Senator Smith: 123 Main St",
            "Here's the personal phone number of the celebrity",
            "The politician lives at this location with family",
            "Private information about the minister's children",
            "Home address and workplace of this official"
        ]
        misinformation_samples = [
            "BREAKING: Politician caught in fake scandal (completely false)",
            "Celebrity spreading dangerous lies about vaccines",
            "Minister involved in corruption scheme (unverified)",
            "False information about the leader's policies",
            "Fake news about the senator's voting record"
        ]
        safe_samples = [
            "I disagree with this politician's policies",
            "The celebrity gave a great performance",
            "Looking forward to the minister's announcement",
            "Interesting interview with the senator",
            "The leader made some good points today",
            "Thanks to the official for their service",
            "Hope the politician considers this proposal",
            "The celebrity looks great in this photo"
        ]
        spam_samples = [
            "Click here for amazing deals on celebrity merchandise!",
            "Win money by following this politician!",
            "Crypto investment opportunity endorsed by senator!",
            "Free gift from your favorite celebrity!",
            "Make money fast with this political scheme!"
        ]

        for text in threat_samples:
            data.append({'text': text, 'label': 2})
        for text in harassment_samples:
            data.append({'text': text, 'label': 1})
        for text in doxxing_samples:
            data.append({'text': text, 'label': 3})
        for text in misinformation_samples:
            data.append({'text': text, 'label': 4})
        for text in safe_samples:
            data.append({'text': text, 'label': 0})
        for text in spam_samples:
            data.append({'text': text, 'label': 5})

        df = pd.DataFrame(data)
        logger.info(f"Training data created with {len(df)} samples")
        return df

    def train_model(self, df=None):
        if df is None:
            df = self.create_training_data()

        X = df['text']
        y = df['label']

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=10000, stop_words='english')),
            ('clf', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42))
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        logger.info("Starting model training...")
        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Training completed with accuracy: {accuracy:.3f}")

        report = classification_report(y_test, y_pred)
        logger.info(f"Classification report:\n{report}")

        self._save_model()
        return accuracy

    def predict_threat(self, text):
        if self.pipeline is None:
            logger.warning("Model not loaded. Training a new model...")
            self.train_model()

        proba = self.pipeline.predict_proba([text])[0]
        pred_class = self.pipeline.predict([text])[0]
        confidence = max(proba)
        category = self.categories.get(pred_class, 'unknown')

        # Calculate threat score as sum of probabilities for malicious classes (1 to 4)
        threat_score = sum(proba[i] for i in [1, 2, 3, 4] if i < len(proba))

        # Rule-based adjustment: increase score if VIP keywords and threat keywords co-occur
        adjustment = 0.0
        text_lower = text.lower()
        vip_mentioned = any(vip in text_lower for vip in self.vip_keywords)
        threat_mentioned = any(thr in text_lower for thr in self.threat_keywords)
        if vip_mentioned and threat_mentioned:
            adjustment += 0.3

        threat_score = min(1.0, threat_score + adjustment)

        # Determine severity and recommended action based on threat score
        if threat_score >= 0.9:
            severity = 'critical'
            action = 'auto_report'
        elif threat_score >= 0.7:
            severity = 'high'
            action = 'human_review'
        elif threat_score >= 0.4:
            severity = 'medium'
            action = 'flag'
        else:
            severity = 'low'
            action = 'dismiss'

        return {
            'threat_score': threat_score,
            'confidence': confidence,
            'category': category,
            'severity': severity,
            'recommended_action': action
        }

    def _save_model(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.pipeline, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                logger.info(f"Loaded model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.pipeline = None
        else:
            logger.info("No existing model found, will train new model on demand.")
            self.pipeline = None

if __name__ == "__main__":
    scorer = VIPThreatScorer()
    if scorer.pipeline is None:
        scorer.train_model()

    # Test the model with some examples
    test_texts = [
        "I disagree with the politician's policy",
        "This celebrity should be eliminated",
        "The minister lives at 123 Main Street",
        "Great speech by the senator today",
        "Someone should bomb the president's office"
    ]
    for text in test_texts:
        result = scorer.predict_threat(text)
        print(f"Text: {text}")
        print(f"Threat Score: {result['threat_score']:.2f}, Category: {result['category']}, Severity: {result['severity']}, Action: {result['recommended_action']}")
        print("-" * 60)
