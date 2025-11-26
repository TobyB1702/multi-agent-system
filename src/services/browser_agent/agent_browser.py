from typing import Optional, Any, List
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

from langchain.agents import create_agent

class AgentBrowser:
    def __init__(self, model: AzureChatOpenAI,tools: List[Any], response_format: Optional[BaseModel] = None):
        self.model = model
        self.tools = tools
        self.response_format = response_format
        self.agent = create_agent(model=self.model, tools=tools, response_format=response_format)
    
    def ask_question(self, question: str) -> str:
        prompt = f"""
        You are a browser agent that can navigate web pages and extract information.
        Your task is to answer the following question: {question}
        Use the tools available to you to gather information and provide a final answer.

        please keep your answer concise and to the point.

        Rules:
        - Take screenshots of each major step you take.
        - Think ahead about which actions to take to answer the question.
        - Limit the amount of Iterations you do to the minimum needed.
        - Keep your final answer short and to the point.
        - Look out for help pages or FAQs on websites that might have the information you need.
        """
        result = self.agent.invoke({"messages": [{"role": "user", "content": prompt}]})

        return result['structured_response']
