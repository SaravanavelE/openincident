import os
import sys
import json
import math
import requests
from typing import List, Dict, Any
from openai import OpenAI

# Environment Variables (Meta Hackathon Requirement)
# Phase 2: API_BASE_URL is for the LLM proxy, ENV_BASE_URL is for the environment
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

# HF_TOKEN Validation
if not HF_TOKEN:
    raise ValueError("HF_TOKEN required")

# LLM Client (Must use HF_TOKEN as api_key for Phase 2)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)


class DevOpsAgent:
    """Hardened LLM-based agent for DevOps incident resolution"""

    def act(self, observation, history):
        prompt = f"""
You are a DevOps incident response agent tasked with resolving service outages in a microservices environment.

Current System Observation:
{json.dumps(observation, indent=2)}

Action History:
{history}

Available Actions:
- check_logs: Retrieve recent system logs to identify the root cause.
- restart_service: Reboot the service (fixes transient crashes).
- scale_up: Increase resource capacity (fixes high load/CPU).
- kill_process: Terminate a specific malfunctioning process (fixes leaks).
- change_config: Apply a configuration patch (fixes drift/errors).
- clear_cache: Purge caches (fixes stale state).

Instructions:
1. Analyze the observation Carefully.
2. Select the single most appropriate action from the list above.
3. Return ONLY the action name, no other text.

Action:"""

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a professional DevOps AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10,
                timeout=8
            )

            action = response.choices[0].message.content.strip().lower()
            
            # Simple validation
            valid_actions = [
                "check_logs", "restart_service", "scale_up", 
                "kill_process", "change_config", "clear_cache"
            ]
            
            for valid in valid_actions:
                if valid in action:
                    return valid
            
            return "check_logs"

        except Exception:
            # Fallback for API failures
            return "check_logs"


def reset_env(task_id):
    """Initializes the environment for a given task"""
    try:
        response = requests.post(
            f"{ENV_BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=30
        )
        data = response.json()
        # Handle both wrapped and unwrapped observations
        return data.get("observation", data)
    except Exception:
        return {}


def step_env(action):
    """Executes an action in the environment"""
    try:
        response = requests.post(
            f"{ENV_BASE_URL}/step",
            json={"action": action},
            timeout=30
        )
        return response.json()
    except Exception:
        return {"observation": {}, "reward": 0.01, "done": True}


def run_evaluation(task_id):
    """Executes a full evaluation episode for a task"""
    observation = reset_env(task_id)
    agent = DevOpsAgent()

    print(f"[START] task={task_id} env=openincident model={MODEL_NAME}")

    history = []
    rewards = []
    total_reward = 0.0
    step_num = 1
    max_steps = 8
    done = False
    success = False

    while not done and step_num <= max_steps:
        action = agent.act(observation, history)
        step_response = step_env(action)

        # Hardened observation parsing
        observation = step_response.get("observation", {})
        if not isinstance(observation, dict):
            observation = {}

        # Hardened reward parsing (Phase-2 compliance: strictly between 0.01 and 0.99)
        reward = step_response.get("reward", 0.01)
        try:
            reward = float(reward)
        except (TypeError, ValueError):
            reward = 0.01
        
        # Clamp strictly between 0.01 and 0.99
        if not math.isfinite(reward):
             reward = 0.01
        reward = min(0.99, max(0.01, reward))

        # Done flag parsing
        done = step_response.get("done", False)
        if isinstance(done, str):
            done = done.lower() == "true"
        else:
            done = bool(done)

        total_reward += reward
        rewards.append(f"{reward:.2f}")

        # Required stdout format
        print(
            f"[STEP]  step={step_num} action={action} reward={reward:.2f} "
            f"done={str(done).lower()} error=null"
        )

        history.append(action)
        step_num += 1
        
        if done:
            success = True

    rewards_str = ",".join(rewards)
    
    # Required [END] format (Strict alignment)
    print(
        f"[END]   success={str(success).lower()} "
        f"steps={step_num-1} "
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

    performance = overall_score / len(tasks)
    # Global score line (informational)
    print(f"--- Global Performance Score: {performance:.2f} ---")
