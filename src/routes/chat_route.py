from fastapi import APIRouter
from src.models.response import AgentResponse
from src.services.orchestrator.tools import OrchestratorAgentToolSets
from src.services.orchestrator.agent_orchestrator import OrchestratorAgent
from src.services.model import model

chat_router = APIRouter()

@chat_router.get("/chat")
async def chat_endpoint(query: str):
    orchestrator_tools = OrchestratorAgentToolSets()
    orchestrator_agent = OrchestratorAgent(model=model, tools=orchestrator_tools.get_tools(), response_format=AgentResponse)
    result = orchestrator_agent.ask_question(query)
    
    return result