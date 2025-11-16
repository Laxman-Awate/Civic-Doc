from pydantic import BaseSettings


class Settings(BaseSettings):
app_name: str = "CivicDoc"
mongodb_uri: str = "mongodb://localhost:27017"
mongodb_db: str = "civicdoc"
model_path: str = "data/models/classifier.pkl"
tfidf_path: str = "data/models/tfidf.pkl"
supported_langs: list = ["en","hi","kn","mr","ta","te"]


class Config:
env_file = ".env"


settings = Settings()