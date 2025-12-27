import sys
from pathlib import Path

# Ensure we can import from apps/api
repo_root = Path(__file__).resolve().parents[1]
api_path = repo_root / "apps" / "api"
sys.path.insert(0, str(api_path))

from agents.registration.agent import RegistrationAgent
from agents.registration.state import RegistrationAgentState, RegistrationStep


def run_test():
    # Create fresh agent state
    state = RegistrationAgentState(
        step=RegistrationStep.COLLECT_PHONE
    )

    agent = RegistrationAgent(state=state)

    agent.handle({"phone_number": "9999999999"})
    '''
    agent.handle({"full_name": "Ajay", "age": 21})
    agent.handle({"symptoms": "Chest pain since morning"})

    agent.handle({})                      # resolve department
    agent.handle({"doctor_id": "doc_1"})  # select doctor
    agent.handle({})   
    '''
    print("\n--- FINAL STATE ---")
    print(state)


if __name__ == "__main__":
    run_test()
