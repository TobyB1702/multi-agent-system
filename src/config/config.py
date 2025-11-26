import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()

class API:
    HOST = os.getenv("API_HOST")
    PORT = os.getenv("API_PORT")

class AzureOpenAI:
    ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    MODEL_NAME = os.getenv("MODEL_NAME")
    DEPLOYMENT = os.getenv("DEPLOYMENT")
    SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY")
    API_VERSION = os.getenv("API_VERSION")

class MetaData:
    SCREENSHOT_PATH = os.getenv("METADATA_SCREENSHOT_PATH", "./screenshots/")
    DATASET_PATH = os.getenv("METADATA_DATASET_PATH", "./datasets/")

class Config:
    API = API
    AZURE_OPENAI = AzureOpenAI
    METADATA = MetaData