from enum import Enum
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field

class ActionEnum(str, Enum):
    CHECK_LOGS = "check_logs"
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    KILL_PROCESS = "kill_process"
    CHANGE_CONFIG = "change_config"
    CLEAR_CACHE = "clear_cache"

class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"

class EnvObservation(BaseModel):
    alert: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    system_status: SystemStatus = SystemStatus.HEALTHY
    cpu_usage: float = 0.0  # Percentage
    memory_usage: float = 0.0  # Percentage

class EnvState(BaseModel):
    step_count: int = 0
    max_steps: int = 10
    incident_resolved: bool = False
    incident_active: bool = True
    current_alert: str
    target_action_sequence: List[ActionEnum]
    action_history: List[ActionEnum] = Field(default_factory=list)
    cpu_usage: float
    memory_usage: float
    system_status: SystemStatus
    logs: List[str] = Field(default_factory=list)
    config_valid: bool = True
    service_running: bool = True
    resource_capacity: int = 1

class StepResponse(BaseModel):
    observation: EnvObservation
    reward: float
    done: bool
    info: Dict[str, Union[str, float, int, bool]] = Field(default_factory=dict)
