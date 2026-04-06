from pydantic import BaseModel
from typing import List, Dict, Any

class TaskConfig(BaseModel):
    id: str = "medium"
    alert: str = "Service 'db-proxy' unreachable after high memory spike."
    target_sequence: List[str] = ["check_logs", "kill_process", "restart_service"]
    initial_stats: Dict[str, float] = {"cpu": 60.0, "memory": 95.0}
    initial_logs: List[str] = ["FATAL: Out of memory killer triggered.", "ERROR: Connection refused."]

# Default task instance
task_data = TaskConfig().dict()
