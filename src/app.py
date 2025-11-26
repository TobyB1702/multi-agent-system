from fastapi import FastAPI
from src.config.config import Config
from src.routes.chat_route import chat_router


app = FastAPI()

app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Multi-Agent System is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API.HOST, port=int(Config.API.PORT))
