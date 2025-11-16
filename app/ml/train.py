"""
Train a simple TF-IDF + XGBoost classifier for complaint category.
This script expects a CSV with columns: text, category, urgency (0/1), severity (0-10)
"""
import argparse
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from pathlib import Path


from app.config import settings




def main(data_csv):
df = pd.read_csv(data_csv)
X = df['text'].fillna("")
y = df['category']


tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1,2))
Xv = tfidf.fit_transform(X)


X_train, X_val, y_train, y_val = train_test_split(Xv, y, test_size=0.2, random_state=42)
clf = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
clf.fit(X_train, y_train)


preds = clf.predict(X_val)
print(classification_report(y_val, preds))


Path(settings.model_path).parent.mkdir(parents=True, exist_ok=True)
joblib.dump(clf, settings.model_path)
joblib.dump(tfidf, settings.tfidf_path)
print("Saved model and tfidf")




if __name__ == '__main__':
parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True)
args = parser.parse_args()
main(args.data)