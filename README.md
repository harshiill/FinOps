# FinOps-Env: Personal Financial Decision-Making Environment

FinOps-Env is a production-grade OpenEnv implementation modeling complex, real-world household financial planning. 

## Motivation
Most LLM agents excel at discrete text tasks but struggle with long-horizon quantitative planning under uncertainty. FinOps-Env tests an agent's ability to balance competing objectives—debt minimization, emergency savings, and budget adherence—over a simulated 12-month period.

## The Environment
* **Domain:** Personal Finance
* **State:** In-memory stochastic simulation of monthly household cash flows.
* **Reward:** Dense (+0.05 for net worth improvements, -0.15 for overdrafts).

## Action Space
Agents submit JSON payloads matching this Pydantic schema:

| Action Type | Description |
|---|---|
| `allocate_budget` | Rebalance deficit categories. |
| `make_payment` | Pay down a specific debt ID. |
| `transfer_funds` | Move cash to savings/goal IDs. |

## Observation Space
Provides full visibility into `month`, `income`, `expenses`, `accounts`, `debts`, `goals`, `credit_score_estimate`, `available_cash`, and monthly `alerts` (e.g., unexpected bills).

## Task Difficulties
1. **Easy:** Budget Rebalancing (Clear deficit reallocation).
2. **Medium:** Debt Payoff Sequencing (Mathematical optimization of interest rates).
3. **Hard:** Multi-Goal Planning (Stochastic income with unexpected medical alerts).

## Project Structure
```text
finops-env/
├── openenv.yaml         # OpenEnv metadata and task definitions
├── requirements.txt     # Python dependencies
├── Dockerfile           # Containerization for Hugging Face Spaces
├── run.sh               # One-click automation script for building and testing
├── README.md            # Project documentation
└── finops_env/          # Core Python package
    ├── __init__.py
    ├── models.py        # Pydantic v2 schemas
    ├── household_generator.py # Procedural state generation
    ├── environment.py   # State transitions and rewards
    ├── graders.py       # Deterministic scoring logic
    ├── main.py          # FastAPI endpoints
    └── baseline.py      # OpenAI ReAct inference script
    
## Automated Run
# 1. Export your OpenAI API Key for the baseline agent
export OPENAI_API_KEY="your-api-key-here"

# 2. Make the script executable (For Linux and MacOS)
chmod +x run.sh

# 3. Run the complete pipeline
./run.sh

##Manual Run
1. Build The Docker Container
   docker build -t finops-env .
   
2.Run the container:
  docker run -p 7860:7860 finops-env
  
3. pip install -r requirements.txt

4.Run the baseline:
export OPENAI_API_KEY="your-api-key-here"
python finops_env/baseline.py

##Baseline Scores
gpt-4o typically achieves ~0.85 on Task 1, ~0.60 on Task 2, and struggles (~0.35) on Task 3 due to the stochastic nature of the income, highlighting the environment's genuine difficulty progression.