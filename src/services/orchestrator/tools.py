from langchain.tools import tool
from src.services.browser_agent.agent_browser import AgentBrowser
from src.services.browser_agent.tools import BrowserAgentToolSets, ToolsContext
from src.logger.logger import logger
from src.config.config import Config
from src.models.response import AgentResponse
from src.services.model import model

class OrchestratorAgentToolSets:
    def get_tools(self):
        """Returns a list of tools in the expected format."""

        @tool
        def call_browser_agent(query: str) -> str:
            """Closes the headless browser session."""
            browser_tools = BrowserAgentToolSets()
            ctx = ToolsContext(Config.METADATA.SCREENSHOT_PATH)
            agent_browser = AgentBrowser(model=model, tools=browser_tools.get_tools(ctx), response_format=AgentResponse)
            logger.info(f"Orchestrator is calling Browser Agent with query: {query}")
            return agent_browser.ask_question(query), ctx.session_dir

        
        return [call_browser_agent]
