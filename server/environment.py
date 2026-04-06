import random
from typing import Dict, Any, List, Optional
from models import EnvState, ActionEnum, EnvObservation, StepResponse, SystemStatus

class OpenIncidentEnv:
    """
    OpenEnv environment for Meta Hackathon.
    Implements reset(), step(), state() to resolve DevOps incidents.
    """
    def __init__(self, task_config: Dict[str, Any] = None):
        self.task_config = task_config or {}
        self.current_state: Optional[EnvState] = None
        self.total_reward = 0.0

    def reset(self, task_id: str = "easy") -> EnvObservation:
        """
        Resets the environment for a new episode.
        task_id: 'easy', 'medium', or 'hard'
        """
        try:
            # Dynamic import of task data
            import importlib
            task_module = importlib.import_module(f"tasks.{task_id}")
            task = task_module.task_data
        except ImportError:
            # Fallback for internal testing
            tasks = {
                "easy": {
                    "alert": "High CPU usage detected on service 'web-api'.",
                    "target_sequence": ["restart_service"],
                    "initial_stats": {"cpu": 85.0, "memory": 40.0},
                    "initial_logs": ["WARN: Resource depletion starting.", "ERROR: Request timeout recurring."]
                }
            }
            task = tasks.get(task_id, tasks["easy"])

        self.current_state = EnvState(
            current_alert=task["alert"],
            target_action_sequence=[ActionEnum(a) for a in task["target_sequence"]],
            cpu_usage=task["initial_stats"]["cpu"],
            memory_usage=task["initial_stats"]["memory"],
            system_status=SystemStatus.WARNING,
            logs=task["initial_logs"],
            max_steps=len(task["target_sequence"]) + 5,
            step_count=0,
            incident_resolved=False,
            incident_active=True
        )
        # Max possible raw reward for normalization: num_steps * 0.2 + 1.0 (resolved)
        self.max_possible_raw_reward = len(task["target_sequence"]) * 0.2 + 1.0
        self.total_raw_reward = 0.0
        return self._get_observation()

    def step(self, action: ActionEnum) -> StepResponse:
        """
        Executes an action in the environment.
        Returns Observation, Reward, Done flag and Info.
        """
        if not self.current_state:
            raise RuntimeError("Environment must be reset before calling step().")

        if not self.current_state.incident_active:
             return StepResponse(
                observation=self._get_observation(),
                reward=0.0,
                done=True,
                info={"message": "Environment is already in a terminal state."}
            )

        self.current_state.step_count += 1
        self.current_state.action_history.append(action)

        step_raw_reward = 0.0
        done = False
        message = ""

        # Logic for target sequence
        target_index = -1
        # Check if the last action was correct in the sequence
        # We find how many correct actions were already taken
        correct_count = 0
        for i, past_action in enumerate(self.current_state.action_history):
             if i < len(self.current_state.target_action_sequence) and past_action == self.current_state.target_action_sequence[i]:
                 correct_count += 1
             else:
                 break
        
        # If the last action moved us forward in the sequence
        last_action_idx = len(self.current_state.action_history) - 1
        if last_action_idx < len(self.current_state.target_action_sequence):
            if action == self.current_state.target_action_sequence[last_action_idx]:
                step_raw_reward += 0.2
                message = f"Correct action: {action}"
                self.current_state.cpu_usage *= 0.9
                self.current_state.memory_usage *= 0.9
            else:
                step_raw_reward -= 0.1
                message = f"Incorrect action: {action}."
        else:
            step_raw_reward -= 0.1
            message = "Unnecessary action."

        # Check if incident is resolved
        if self._is_task_completed():
            step_raw_reward += 1.0
            self.current_state.incident_resolved = True
            self.current_state.incident_active = False
            self.current_state.system_status = SystemStatus.HEALTHY
            done = True
            message = "Incident resolved successfully."

        # Check for timeout
        elif self.current_state.step_count >= self.current_state.max_steps:
            step_raw_reward -= 0.5
            self.current_state.incident_active = False
            done = True
            message = "Timeout: Maximum steps exceeded."

        # Track total raw reward
        self.total_raw_reward += step_raw_reward
        
        # Normalize reward returned for this step.
        # OpenEnv hackathon asks for total reward between 0-1.
        # We ensure the raw step reward, when scaled by max possible, fits this.
        normalized_step_reward = max(0.0, step_raw_reward / self.max_possible_raw_reward)

        return StepResponse(
            observation=self._get_observation(),
            reward=round(normalized_step_reward, 3),
            done=done,
            info={"message": message, "step": self.current_state.step_count}
        )

    def state(self) -> Dict[str, Any]:
        """
        Returns full internal state.
        """
        return self.current_state.dict() if self.current_state else {}

    def _get_observation(self) -> EnvObservation:
        """
        Extracts parts of the state visible to the agent.
        """
        return EnvObservation(
            alert=self.current_state.current_alert if self.current_state.incident_active else "System Healthy",
            logs=self.current_state.logs[-5:], # Last 5 logs
            system_status=self.current_state.system_status,
            cpu_usage=round(self.current_state.cpu_usage, 2),
            memory_usage=round(self.current_state.memory_usage, 2)
        )

    def _is_task_completed(self) -> bool:
        """Check if all required actions were performed in order."""
        return self.current_state.action_history[-len(self.current_state.target_action_sequence):] == self.current_state.target_action_sequence

    def _normalize_reward(self, step_reward: float) -> float:
        """
        Adjust reward to follow the 0.0 - 1.0 range constraint.
        Since total reward is expected to be [0,1], 
        we make per-step rewards smaller or return only fractions.
        """
        # For simplicity, we keep step_reward and user can normalize, 
        # but the spec asks for reward between 0-1.
        # I'll return it as a fraction of the max possible total.
        # Or just cap it between 0 and 1 for each step.
        return max(0.0, min(1.0, step_reward)) # This is per-step.
