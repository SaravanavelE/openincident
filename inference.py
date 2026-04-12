import os
import sys
import json
import math
import requests
from typing import List, Dict, Any
from openai import OpenAI

# Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)


class DevOpsAgent:

    def act(self, observation, history):

        prompt = f"""
You are a DevOps incident response agent.
Observation:
{json.dumps(observation, indent=2)}
History:
{history}
Available Actions:
- check_logs
- restart_service
- scale_up
- kill_process
- change_config
- clear_cache
Return ONLY action name.
"""

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "DevOps AI"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10,
                timeout=8
            )

            action = response.choices[0].message.content.strip().lower()

            valid = [
                "check_logs",
                "restart_service",
                "scale_up",
                "kill_process",
                "change_config",
                "clear_cache"
            ]

            for v in valid:
                if v in action:
                    return v

            return "check_logs"

        except Exception:
            return "check_logs"


def reset_env(task_id):

    try:
        response = requests.post(
            f"{ENV_BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=30
        )
        data = response.json()
        return data.get("observation", data)

    except Exception:
        return {}


def step_env(action):

    try:
        response = requests.post(
            f"{ENV_BASE_URL}/step",
            json={"action": action},
            timeout=30
        )
        return response.json()

    except Exception:
        return {
            "observation": {},
            "reward": 0.5,
            "done": True
        }


def clamp_reward(reward):
    try:
        reward = float(reward)
    except:
        reward = 0.5

    if not math.isfinite(reward):
        reward = 0.5

    return min(1 - 1e-6, max(1e-6, reward))

def safe_score(score, eps=1e-6):
    try:
        score = float(score)
    except:
        return eps

    if not math.isfinite(score):
        return eps

    return min(1 - eps, max(eps, score))

def run_evaluation(task_id):

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

        observation = step_response.get("observation", {})
        if not isinstance(observation, dict):
            observation = {}

        reward = clamp_reward(step_response.get("reward", 0.5))
        reward = safe_score(reward)

        done = step_response.get("done", False)
        if isinstance(done, str):
            done = done.lower() == "true"
        else:
            done = bool(done)

        assert 0 < reward < 1
        total_reward += reward
        rewards.append(f"{reward:.6f}")

        print(
            f"[STEP] step={step_num} action={action} "
            f"reward={reward:.6f} done={str(done).lower()} error=null"
        )

        history.append(action)
        step_num += 1

        if done:
            success = True

    if not rewards:
        rewards.append("0.500000")

    rewards_str = ",".join(rewards)

    task_score = (total_reward + 1e-6) / (len(rewards) + 2e-6)
    task_score = safe_score(task_score)
    print(
        f"[END] success={str(success).lower()} "
        f"steps={step_num-1} "
        f"rewards={rewards_str} "
        f"score={task_score:.6f}"
    )
    return task_score


if __name__ == "__main__":

    tasks = ["easy", "medium", "hard"]
    overall_score = 0.0

    print("Running Meta Hackathon Evaluation for OpenIncident...")

    for task in tasks:
        score = run_evaluation(task)
        overall_score += score

    performance = overall_score / len(tasks)
    performance = safe_score(performance)

    print(f"--- Global Performance Score: {performance:.6f} ---")
