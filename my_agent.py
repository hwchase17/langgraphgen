# my_agent.py
from generated_agent import GeneratedAgent
from pydantic import BaseModel

class AgentState(BaseModel):
    counter: int = 0
    result: str = ""

class MyAgent(GeneratedAgent):
    @property
    def state_schema(self) -> type[BaseModel]:
        return AgentState  # Use the same schema for input/output

    def start(self, state: AgentState) -> AgentState:
        state.result = f"Processed {state.counter} times"
        return state

    # Implement other nodes...

    def process(self, state: dict) -> dict:
        print("Processing...")
        state.counter += 1
        return state

    def decide(self, state: dict) -> dict:
        print("Deciding...")
        return state

    def check_decision(self, state: dict) -> str:
        return "end" if state.counter >= 3 else "continue"

# Usage
agent = MyAgent()
response = agent.app.invoke({"counter": 0})
print(response)
