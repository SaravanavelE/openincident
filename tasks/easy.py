from pydantic import BaseModel
from typing import List, Dict, Any

class TaskConfig(BaseModel):
    id: str = "easy"
    alert: str = "High CPU usage detected on service 'web-api'."
    target_sequence: List[str] = ["restart_service"]
    initial_stats: Dict[str, float] = {"cpu": 85.0, "memory": 40.0}
    initial_logs: List[str] = ["WARN: Resource depletion starting.", "ERROR: Request timeout recurring."]

# Default task instance
task_data = TaskConfig().dict()
