from langchain_openai import AzureChatOpenAI
from src.config.config import Config

model = AzureChatOpenAI(
    azure_deployment=Config.AZURE_OPENAI.DEPLOYMENT,
    api_version=Config.AZURE_OPENAI.API_VERSION,
    azure_endpoint=Config.AZURE_OPENAI.ENDPOINT,
    api_key=Config.AZURE_OPENAI.SUBSCRIPTION_KEY,
    seed=42)