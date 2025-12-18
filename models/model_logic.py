import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import re
import string

# Enhanced Synthetic data with Roman Urdu support
data = {
    'text': [
        'My internet is not working', 'WiFi connection is slow', 'Server not reachable', 'Technical glitch in website',
        'Net nahi chal raha', 'Wifi masla kar raha hai', 'Link down hai', 'Speed slow hai',
        'Billing error in my statement', 'I was charged twice', 'Payment not reflected', 'Refund status for my bill',
        'Bill me galti hai', 'Double paise kat gaye', 'Payment show nahi ho rahi', 'Refund chahiye',
        'Delivery is late', 'Product not received', 'Package was damaged', 'Tracking ID not working',
        'Delivery late hai', 'Saman nahi mila', 'Parcel kharab hai', 'Tracking nahi ho rahi',
        'General inquiry about working hours', 'How to contact support', 'Need help with account', 'Feedback on service',
        'Timing kya hai', 'Help chahiye', 'Service achi nahi hai', 'Shikayat karni hai'
    ],
    'category': [
        'Technical', 'Technical', 'Technical', 'Technical',
        'Technical', 'Technical', 'Technical', 'Technical',
        'Billing', 'Billing', 'Billing', 'Billing',
        'Billing', 'Billing', 'Billing', 'Billing',
        'Delivery', 'Delivery', 'Delivery', 'Delivery',
        'Delivery', 'Delivery', 'Delivery', 'Delivery',
        'General', 'General', 'General', 'General',
        'General', 'General', 'General', 'General'
    ]
}

# Mapping category to priority and department
CATEGORY_CONFIG = {
    'Technical': {
        'priority': 'High', 
        'department': 'IT Support', 
        'response_time': '2-4 hours'
    },
    'Billing': {
        'priority': 'Medium', 
        'department': 'Accounts', 
        'response_time': '12-24 hours'
    },
    'Delivery': {
        'priority': 'High', 
        'department': 'Logistics', 
        'response_time': '4-8 hours'
    },
    'General': {
        'priority': 'Low', 
        'department': 'Customer Service', 
        'response_time': '1-2 business days'
    }
}

def preprocess_text(text):
    text = str(text).lower()
    # Remove punctuation
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    # Basic tokenization and stopword removal (simplified for small data)
    return text

def train_model():
    df = pd.DataFrame(data)
    df['text'] = df['text'].apply(preprocess_text)
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression())
    ])
    
    pipeline.fit(df['text'], df['category'])
    
    # Save model and mapping
    joblib.dump(pipeline, 'models/complaint_model.joblib')
    print("Model trained with extended dataset and saved.")

def predict_complaint(text):
    try:
        model = joblib.load('models/complaint_model.joblib')
        clean_text = preprocess_text(text)
        category = model.predict([clean_text])[0]
        
        config = CATEGORY_CONFIG.get(category, {
            'priority': 'Medium', 
            'department': 'General', 
            'response_time': '24-48 hours'
        })
        return category, config['priority'], config['department'], config['response_time']
    except Exception as e:
        print(f"Prediction error: {e}")
        return "General", "Medium", "Customer Service", "24-48 hours"

if __name__ == "__main__":
    train_model()
