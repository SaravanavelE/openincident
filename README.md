---
title: OpenIncident
emoji: 🚨
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---


# OpenIncident — DevOps Incident Response Environment

OpenIncident is a high-fidelity DevOps simulation specifically designed for the **Meta PyTorch OpenEnv Hackathon**. It challenges AI agents to act as DevOps responders resolving service outages in a microservices environment.

## 🏛️ Architecture

OpenIncident follows the standard **OpenEnv HTTP protocol**. It is split into:
- **Server**: A FastAPI-based environment that simulates system states, metrics (CPU/RAM), and logs.
- **Tasks**: Hierarchical incidents with increasing difficulty (Single point → Multi-step leak → Cascading failover).
- **Core Engine**: A deterministic state machine that transitions based on discrete actions.

## 🛠️ Action Space
Agents can perform the following actions:
- `check_logs`: Retrieve recent system logs.
- `restart_service`: Attempt to reboot the failed service.
- `scale_up`: Provision extra resources to handle load.
- `kill_process`: Terminate a malfunctioning or leaking process.
- `change_config`: Apply a configuration patch to fix drift.
- `clear_cache`: Purge local and distributed caches.

## 👁️ Observation Space
The environment returns a state observation containing:
- `alert`: The current active system alert (string).
- `logs`: Last 5 lines of system logs (list of strings).
- `system_status`: `healthy`, `warning`, `critical`, or `down`.
- `cpu_usage`: Real-time CPU utilization (0.0% - 100.0%).
- `memory_usage`: Real-time Memory utilization (0.0% - 100.0%).

## 🎯 Tasks & Baseline Scores

| Task   | Difficulty | Goal | Optimal Steps | Probable Score (Rule-Based) |
| :---   | :---:      | :--- | :---:         | :---:                       |
| Easy   | 🟢 Easy    | Service Restart | 1 | 1.00 |
| Medium | 🟡 Medium  | Memory Leak Fix | 3 | 1.00 |
| Hard   | 🔴 Hard    | Cascading Drift | 4 | 0.90 |

*Scores are normalized between 0.0 — 1.0.*

## 🚀 Setup Instructions

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the environment
python server/app.py

# In another terminal, run evaluation
python inference.py
```

### HuggingFace Spaces Deployment
1. Build the Docker image: `docker build -t openincident .`
2. Run locally: `docker run -p 7860:7860 openincident`
3. Push to HF Space: Simply upload `Dockerfile`, `server/`, `tasks/`, `models.py`, `requirements.txt`, and `openenv.yaml`.

## 📡 API Endpoints (OpenEnv Compatible)
- `POST /reset?task_id=easy`: Initialize the task.
- `POST /step`: Submit an action.
- `GET /state`: View full environment state.
- `GET /health`: Check server status.
