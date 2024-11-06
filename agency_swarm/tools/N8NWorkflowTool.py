# agency_swarm/tools/N8NWorkflowTool.py
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import os

class N8NWorkflowTool(BaseTool):
    workflow_id: str = Field(..., description="N8N workflow ID or endpoint path.")
    payload: dict = Field(default={}, description="Data payload for triggering workflows.")

    def run(self):
        n8n_url = os.getenv("N8N_BASE_URL")  # Ensure N8N's base URL is set
        url = f"{n8n_url}/webhook/{self.workflow_id}"
        response = requests.post(url, json=self.payload)
        return response.json() if response.ok else f"Error: {response.text}"
