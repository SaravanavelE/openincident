from pydantic import BaseModel
from typing import List, Dict, Any

class TaskConfig(BaseModel):
    id: str = "hard"
    alert: str = "Microservice cascading failure: Suspected config drift on 'auth-gateway'."
    target_sequence: List[str] = ["change_config", "restart_service", "scale_up", "clear_cache"]
    initial_stats: Dict[str, float] = {"cpu": 90.0, "memory": 88.0}
    initial_logs: List[str] = ["ERR: Invalid sequence in config.", "WARN: Cluster nodes dropping out."]

# Default task instance
task_data = TaskConfig().dict()
