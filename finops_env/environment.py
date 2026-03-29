import random
from typing import Dict, Any, Tuple
from .models import FinancialObservation, FinancialAction, EnvState, AccountState
from .household_generator import HouseholdGenerator

class FinOpsEnv:
    """Core environment managing state transitions and rewards."""
    
    def __init__(self):
        self.state: EnvState = None
        self.max_months = 12
        self.starting_total_debt = 0.0
        
    def reset(self, task_id: str) -> FinancialObservation:
        data = HouseholdGenerator.generate(task_id)
        
        available_cash = sum(acc.balance for acc in data["accounts"] if acc.account_type == "checking")
        
        obs = FinancialObservation(
            month=data["month"],
            income=data["income"],
            expenses=data["expenses"],
            accounts=data["accounts"],
            debts=data["debts"],
            goals=data["goals"],
            credit_score_estimate=data["credit_score_estimate"],
            available_cash=available_cash,
            alerts=data["alerts"]
        )
        
        self.starting_total_debt = sum(d.principal_balance for d in data["debts"])
        self.base_income = data["base_income"]
        
        self.state = EnvState(
            observation=obs,
            task_id=task_id,
            is_done=False,
            total_reward=0.0,
            metrics={"total_interest_paid": 0.0, "missed_payments": 0, "actions_taken": 0, "overdrafts": 0}
        )
        return self.state.observation

    def step(self, action: FinancialAction) -> Tuple[FinancialObservation, float, bool, Dict[str, Any]]:
        if self.state.is_done:
            raise ValueError("Episode is already done. Please reset.")
            
        obs = self.state.observation
        reward = 0.0
        self.state.metrics["actions_taken"] += 1
        
        # Action Logic
        if action.action_type == "make_payment" and action.account_id:
            for debt in obs.debts:
                if debt.account_id == action.account_id:
                    if obs.available_cash >= action.amount:
                        obs.available_cash -= action.amount
                        debt.principal_balance -= action.amount
                        reward += 0.05  # Positive trajectory
                    else:
                        reward -= 0.15  # Overdraft attempt
                        self.state.metrics["overdrafts"] += 1

        elif action.action_type == "transfer_funds" and action.account_id:
            if action.account_id.startswith("g_"): # Goal contribution
                for goal in obs.goals:
                    if goal.goal_id == action.account_id and obs.available_cash >= action.amount:
                        obs.available_cash -= action.amount
                        goal.current_amount += action.amount
                        reward += 0.05
                        
        elif action.action_type == "allocate_budget" and action.category:
                    if action.category in obs.expenses and action.amount > 0:
                        # Reduce deficit
                        obs.expenses[action.category] -= action.amount 
                        reward += 0.02 # Give a step reward for successfully cutting expenses
                
        # End of Month Simulation (if 5 actions taken or explicit end_month action implemented)
        # For hackathon simplicity, let's auto-advance month every 3 actions
        if self.state.metrics["actions_taken"] % 3 == 0:
            obs.month += 1
            obs.alerts.clear()
            
            # Stochastic income for Task 3
            if self.state.task_id == "task_3_hard":
                obs.income = self.base_income * random.uniform(0.85, 1.15)
            
            # Apply interest and check minimums
            for debt in obs.debts:
                if debt.principal_balance > 0:
                    interest = debt.principal_balance * (debt.interest_rate / 12)
                    debt.principal_balance += interest
                    self.state.metrics["total_interest_paid"] += interest
                    # Simplified min payment check
                    if debt.principal_balance > 0 and action.action_type != "make_payment": 
                        reward -= 0.10
                        self.state.metrics["missed_payments"] += 1
            
            # Add base income to cash
            obs.available_cash += obs.income - sum(obs.expenses.values())
            
            # Emergency fund check
            em_fund = next((g.current_amount for g in obs.goals if g.goal_type == "emergency_fund"), 0)
            if em_fund > self.base_income:
                reward += 0.02

        # Check Termination
        if obs.month >= self.max_months:
            self.state.is_done = True
            
        # Update checking account to reflect available cash
        for acc in obs.accounts:
            if acc.account_type == "checking":
                acc.balance = obs.available_cash

        self.state.total_reward += reward
        self.state.observation = obs
        
        return self.state.observation, reward, self.state.is_done, self.state.metrics

    def get_state(self) -> EnvState:
        return self.state