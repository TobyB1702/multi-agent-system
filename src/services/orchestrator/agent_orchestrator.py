from pathlib import Path
from typing import Optional, Any, List
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel


from langchain.agents import create_agent
from src.logger.logger import logger
from datetime import datetime

import pandas as pd

class OrchestratorAgent:
    def __init__(self, model: AzureChatOpenAI,tools: List[Any], response_format: Optional[BaseModel] = None, dataset_path: str = "datasets/agent_logs.csv"):
        self.model = model
        self.tools = tools
        self.response_format = response_format
        self.agent = create_agent(model=self.model, tools=tools, response_format=response_format)
        self.dataset_path = Path(dataset_path)

        self._initialize_dataset()

    def _initialize_dataset(self) -> None:
        """Create dataset CSV file with header if it doesn't exist."""
        if not self.dataset_path.exists():
            self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(columns=["timestamp", "question", "answer", "session_dir"])
            df.to_csv(self.dataset_path, index=False)
            logger.info(f"Created new dataset CSV file: {self.dataset_path}")

    def _log_interaction(self, question: str, answer: str, session_dir: str) -> None:
        """Log agent interaction to CSV (appends a new row)."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "session_dir": str(session_dir)
        }

        try:
            # Ensure parent dir exists
            self.dataset_path.parent.mkdir(parents=True, exist_ok=True)

            df = pd.DataFrame([log_entry])
            write_header = not self.dataset_path.exists() or self.dataset_path.stat().st_size == 0
            df.to_csv(self.dataset_path, mode="a", header=write_header, index=False)
            logger.info(f"Logged interaction to {self.dataset_path}")
        except Exception as e:
            logger.error(f"Error logging interaction to CSV: {str(e)}")
    
    def ask_question(self, question: str) -> str:
        prompt = f"""
        You are an orchestrator agent that can coordinate multiple browser agents to navigate web pages and extract information.
        Your task is to answer the following question: {question}
        Use the tools available to you to gather information and provide a final answer.

        please keep your answer concise and to the point.

        Rules:
        - Limit the amount of Iterations you do to the minimum needed.
        - Keep your final answer short and to the point.
        - Only use the browser agents when needed.
        - If the user asks a technical question, use the browser agents to find up-to-date information.
        """
        result = self.agent.invoke({"messages": [{"role": "user", "content": prompt}]})['structured_response']
        self._log_interaction(question, result.final_answer, result.session_dir)

        return result
