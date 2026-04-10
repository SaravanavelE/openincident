import requests
from typing import Dict, Any, List, Optional
from models import ActionEnum, EnvObservation, StepResponse

class OpenIncidentClient:
    """ Client to communicate with the OpenIncident server. """
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url

    def reset(self, task_id: str = "easy") -> EnvObservation:
        response = requests.post(f"{self.base_url}/reset", params={"task_id": task_id})
        response.raise_for_status()
        return EnvObservation(**response.json())

    def step(self, action: ActionEnum) -> StepResponse:
        # FastAPI expects action as a JSON string in body
        response = requests.post(f"{self.base_url}/step", json={"action": action.value})
        response.raise_for_status()
        return StepResponse(**response.json())

    def state(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/state")
        response.raise_for_status()
        return response.json()
