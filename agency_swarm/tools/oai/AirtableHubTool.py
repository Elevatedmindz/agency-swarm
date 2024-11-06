# agency_swarm/tools/AirtableHubTool.py
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import os

class AirtableHubTool(BaseTool):
    base_id: str = Field(..., description="Airtable base ID.")
    table_name: str = Field(..., description="Airtable table name to query.")
    action: str = Field(..., description="Action: 'get' or 'update'.")
    record_id: str = Field(None, description="Record ID for updates.")
    data: dict = Field(None, description="Data to update (used only for 'update' action).")

    def run(self):
        api_key = os.getenv("AIRTABLE_API_KEY")  # Ensure this is set in your environment
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        headers = {"Authorization": f"Bearer {api_key}"}

        if self.action == "get":
            response = requests.get(url, headers=headers)
        elif self.action == "update" and self.record_id:
            url = f"{url}/{self.record_id}"
            response = requests.patch(url, headers=headers, json={"fields": self.data})
        else:
            return "Invalid action or missing record_id."
        
        return response.json() if response.ok else response.text
