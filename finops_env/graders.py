from .models import EnvState

class Grader:
    """Deterministic graders for each task returning a 0.0 to 1.0 score."""
    
    @staticmethod
    def grade_task_1(state: EnvState) -> float:
        """Score = (deficit_eliminated * 0.6) + (categories_balanced * 0.4)"""
        obs = state.observation
        # Assuming initial deficits were in entertainment, dining_out, subscriptions
        target_expenses = ["entertainment", "dining_out", "subscriptions"]
        
        eliminated_score = 0.0
        balanced_count = 0
        
        for cat in target_expenses:
            current_val = obs.expenses.get(cat, 0)
            # If expense is brought down to a reasonable level (e.g., < 5% of income)
            if current_val < (obs.income * 0.05):
                eliminated_score += (1.0 / len(target_expenses))
                balanced_count += 1
                
        balanced_score = balanced_count / len(target_expenses)
        return round((eliminated_score * 0.6) + (balanced_score * 0.4), 4)

    @staticmethod
    def grade_task_2(state: EnvState) -> float:
        """Score = 1.0 - (actual_interest_paid / worst_case_interest_paid)"""
        actual_interest = state.metrics.get("total_interest_paid", 0)
        # Rough heuristic for worst case: making zero payments for 12 months
        # Approximated based on starting principal. In a real scenario, this would be passed from env.
        worst_case_interest = actual_interest + 5000.0 # Bounded scalar for hackathon
        
        if worst_case_interest <= 0:
            return 1.0
            
        score = max(0.0, 1.0 - (actual_interest / worst_case_interest))
        return round(score, 4)

    @staticmethod
    def grade_task_3(state: EnvState) -> float:
        """Weighted average of various financial health metrics."""
        obs = state.observation
        
        em_fund = next((g for g in obs.goals if g.goal_type == "emergency_fund"), None)
        em_score = min(1.0, em_fund.current_amount / em_fund.target_amount) if em_fund else 0.0
        
        ret_fund = next((g for g in obs.goals if g.goal_type == "retirement"), None)
        ret_score = min(1.0, ret_fund.current_amount / 20000) if ret_fund else 0.0 # Based on 12 month progress
        
        col_fund = next((g for g in obs.goals if g.goal_type == "college"), None)
        col_score = min(1.0, col_fund.current_amount / 2000) if col_fund else 0.0 # Based on 12 month progress
        
        debt_score = 1.0 if state.metrics.get("missed_payments", 0) == 0 else 0.0
        cash_flow_score = 1.0 if state.metrics.get("overdrafts", 0) == 0 else 0.0
        
        final_score = (em_score * 0.25) + (ret_score * 0.30) + (col_score * 0.20) + (debt_score * 0.15) + (cash_flow_score * 0.10)
        return round(final_score, 4)

    @classmethod
    def grade(cls, state: EnvState) -> float:
        if state.task_id == "task_1_easy":
            return cls.grade_task_1(state)
        elif state.task_id == "task_2_medium":
            return cls.grade_task_2(state)
        elif state.task_id == "task_3_hard":
            return cls.grade_task_3(state)
        return 0.0