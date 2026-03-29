import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Ensure your OPENAI_API_KEY is set in your environment
client = OpenAI()
BASE_URL = "http://localhost:7860"

def run_baseline():
    print("Starting OpenEnv Baseline Run...")
    tasks = requests.get(f"{BASE_URL}/tasks").json()["tasks"]
    
    for task_id in tasks:
        print(f"\n--- Running Task: {task_id} ---")
        obs = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id}).json()
        done = False
        step_count = 0
        
        while not done and step_count < 36: # Max 3 actions * 12 months
            prompt = f"""
                        You are an expert financial AI agent. 
                        Current observation: {json.dumps(obs, indent=2)}
                        Task ID: {task_id}
                        
                        STRATEGY GUIDE:
                        - If task_1_easy: Your goal is to use 'allocate_budget' to reduce high expenses (like entertainment, dining_out, subscriptions). Set the 'category' to the expense name and 'amount' to how much you want to reduce it by.
                        - If task_2_medium: Your goal is to use 'make_payment' to pay off high-interest debt.
                        - If task_3_hard: Balance debt payments ('make_payment') with saving for goals ('transfer_funds' to goal IDs).
                        
                        Based on the observation, output a JSON action to improve the financial state.
                        Must match this schema exactly:
                        {{
                            "action_type": "allocate_budget" | "make_payment" | "transfer_funds",
                            "category": "string (optional, use for budget category)",
                            "amount": float,
                            "account_id": "string (optional, use for debt or goal ID)"
                        }}
                        Output ONLY valid JSON.
                        """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            try:
                action = json.loads(response.choices[0].message.content)
                step_res = requests.post(f"{BASE_URL}/step", json=action).json()
                obs = step_res["observation"]
                done = step_res["done"]
                print(f"Step {step_count}: Action={action['action_type']}, Reward={step_res['reward']}")
            except Exception as e:
                print(f"Agent generated invalid action format. Error: {e}")
                break
                
            step_count += 1
            
        final_score = requests.get(f"{BASE_URL}/grader").json()["score"]
        print(f"Finished {task_id}. Final Grader Score: {final_score}")

if __name__ == "__main__":
    run_baseline()