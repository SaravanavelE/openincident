import os
import sys
import json
import requests
from typing import List, Dict, Any

# Environment Variables (Meta Hackathon Requirement)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "rule-based")
HF_TOKEN = os.getenv("HF_TOKEN", "")


class RuleBasedAgent:
    """Simple baseline agent for DevOps incident resolution"""

    def act(self, observation, history):

        alert = observation.get("alert", "").lower()

        # CPU issue
        if "cpu" in alert and "restart_service" not in history:
            return "restart_service"

        # Memory issue
        if "memory" in alert:
            if "kill_process" not in history:
                return "kill_process"
            if "restart_service" not in history:
                return "restart_service"

        # Config issue
        if "config" in alert:
            if "change_config" not in history:
                return "change_config"
            if "restart_service" not in history:
                return "restart_service"

        return "check_logs"


def reset_env(task_id):
    response = requests.post(
        f"{API_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30
    )
    return response.json()


def step_env(action):
    response = requests.post(
        f"{API_BASE_URL}/step",
        json={"action": action},
        timeout=30
    )
    return response.json()


def run_evaluation(task_id):

    observation = reset_env(task_id)

    agent = RuleBasedAgent()

    print(f"[START] task={task_id} env=openincident model={MODEL_NAME}")

    history = []
    rewards = []
    total_reward = 0.0

    step_num = 1
    done = False
    success = False

    while not done:

        action = agent.act(observation, history)

        step_response = step_env(action)

        observation = step_response.get("observation", {})
        reward = step_response.get("reward", 0.0)
        done = step_response.get("done", False)

        total_reward += reward
        rewards.append(f"{reward:.2f}")

        print(
            f"[STEP] step={step_num} action={action} reward={reward:.2f} "
            f"done={str(done).lower()} error=null"
        )

        history.append(action)
        step_num += 1

        if done:
            success = True

    rewards_str = ",".join(rewards)

    print(
        f"[END] success={str(success).lower()} "
        f"steps={step_num-1} "
        f"score={total_reward:.2f} "
        f"rewards={rewards_str}"
    )

    return total_reward


if __name__ == "__main__":

    tasks = ["easy", "medium", "hard"]

    overall_score = 0.0

    print("Running Meta Hackathon Evaluation for OpenIncident...")

    for task in tasks:
        score = run_evaluation(task)
        overall_score += score

    print(f"--- Global Performance Score: {overall_score / len(tasks):.2f} ---")
