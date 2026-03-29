import random
import uuid
from typing import Dict, Any
from .models import AccountState, DebtState, GoalProgress

class HouseholdGenerator:
    """Procedurally generates varied households for the FinOps environment."""
    
    @staticmethod
    def generate(task_id: str) -> Dict[str, Any]:
        """Generates a fresh household state tailored to the task."""
        income_bracket = random.choice(["low", "medium", "high"])
        base_income = {"low": 3500, "medium": 6000, "high": 12000}[income_bracket]
        income = base_income * random.uniform(0.9, 1.1)
        
        # Base accounts
        accounts = [
            AccountState(account_id=str(uuid.uuid4())[:8], account_type="checking", balance=income * random.uniform(0.5, 1.5)),
            AccountState(account_id=str(uuid.uuid4())[:8], account_type="savings", balance=income * random.uniform(0.1, 2.0))
        ]
        
        # Debts and Goals vary by task
        debts = []
        goals = []
        expenses = {"housing": income * 0.3, "food": income * 0.15, "utilities": income * 0.1}
        
        if task_id == "task_1_easy":
            # Introduce a deficit in specific categories
            expenses["entertainment"] = income * 0.2
            expenses["dining_out"] = income * 0.15
            expenses["subscriptions"] = income * 0.1
        
        elif task_id == "task_2_medium":
            debts = [
                DebtState(account_id="cc_1", debt_type="credit_card", principal_balance=5000, interest_rate=0.22, minimum_payment=150),
                DebtState(account_id="sl_1", debt_type="student_loan", principal_balance=25000, interest_rate=0.06, minimum_payment=250),
                DebtState(account_id="car_1", debt_type="car_loan", principal_balance=15000, interest_rate=0.08, minimum_payment=350),
                DebtState(account_id="med_1", debt_type="medical", principal_balance=2000, interest_rate=0.0, minimum_payment=50)
            ]
            
        elif task_id == "task_3_hard":
            debts = [DebtState(account_id="cc_1", debt_type="credit_card", principal_balance=3000, interest_rate=0.24, minimum_payment=100)]
            goals = [
                GoalProgress(goal_id="g_em", goal_type="emergency_fund", current_amount=1000, target_amount=income * 3),
                GoalProgress(goal_id="g_ret", goal_type="retirement", current_amount=15000, target_amount=100000),
                GoalProgress(goal_id="g_col", goal_type="college", current_amount=0, target_amount=20000)
            ]
            # Unexpected medical bill is an alert, not a base debt yet
            
        return {
            "month": 1,
            "base_income": income,
            "income": income,
            "expenses": expenses,
            "accounts": accounts,
            "debts": debts,
            "goals": goals,
            "credit_score_estimate": random.uniform(600, 750),
            "alerts": ["Welcome to Month 1."] if task_id != "task_3_hard" else ["Unexpected medical bill: $1500 due in 3 months."]
        }