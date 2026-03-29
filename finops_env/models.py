from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

class AccountState(BaseModel):
    account_id: str
    account_type: Literal["checking", "savings", "emergency", "investment"]
    balance: float

class DebtState(BaseModel):
    account_id: str
    debt_type: Literal["credit_card", "student_loan", "car_loan", "medical"]
    principal_balance: float
    interest_rate: float
    minimum_payment: float

class GoalProgress(BaseModel):
    goal_id: str
    goal_type: Literal["emergency_fund", "retirement", "college"]
    current_amount: float
    target_amount: float

class FinancialObservation(BaseModel):
    month: int
    income: float
    expenses: Dict[str, float]
    accounts: List[AccountState]
    debts: List[DebtState]
    goals: List[GoalProgress]
    credit_score_estimate: float
    available_cash: float
    alerts: List[str]

class FinancialAction(BaseModel):
    action_type: Literal["allocate_budget", "make_payment", "open_account", "transfer_funds", "adjust_contribution"]
    category: Optional[str] = Field(default=None, description="Budget category, if applicable")
    amount: float = Field(..., description="Amount of money involved in the action")
    account_id: Optional[str] = Field(default=None, description="Target account or debt ID")
    source_account_id: Optional[str] = Field(default=None, description="Source account for transfers")

class StepReward(BaseModel):
    step_reward: float
    info: Dict[str, float]

class EnvState(BaseModel):
    observation: FinancialObservation
    task_id: str
    is_done: bool
    total_reward: float
    metrics: Dict[str, float]