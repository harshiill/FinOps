import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from .models import FinancialAction, FinancialObservation, EnvState
from .environment import FinOpsEnv
from .graders import Grader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FinOps-Env OpenEnv API")
env_instance = FinOpsEnv()

class ResetRequest(BaseModel):
    task_id: str

class StepResponse(BaseModel):
    observation: FinancialObservation
    reward: float
    done: bool
    info: Dict[str, Any]

@app.get("/tasks")
def get_tasks():
    logger.info("Tasks requested")
    return {
        "tasks": ["task_1_easy", "task_2_medium", "task_3_hard"],
        "action_schema": FinancialAction.model_json_schema()
    }

@app.post("/reset", response_model=FinancialObservation)
def reset_env(req: ResetRequest):
    if req.task_id not in ["task_1_easy", "task_2_medium", "task_3_hard"]:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    logger.info(f"Resetting environment for {req.task_id}")
    return env_instance.reset(req.task_id)

@app.post("/step", response_model=StepResponse)
def step_env(action: FinancialAction):
    if env_instance.state is None or env_instance.state.is_done:
        raise HTTPException(status_code=400, detail="Environment not initialized or episode done. Call /reset.")
    
    logger.info(f"Taking action: {action.action_type}")
    obs, reward, done, info = env_instance.step(action)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/state", response_model=EnvState)
def get_state():
    if env_instance.state is None:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    return env_instance.get_state()

@app.get("/grader")
def get_grade():
    if env_instance.state is None:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    score = Grader.grade(env_instance.get_state())
    return {"score": score, "task_id": env_instance.state.task_id}

@app.get("/health")
def healthcheck():
    return {"status": "ok"}