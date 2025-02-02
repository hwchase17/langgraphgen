from abc import ABC, abstractmethod
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class GeneratedAgent(ABC):
    def __init__(self):
        self.graph = StateGraph(self.state_schema)
        self._build_graph()
        self.app = self.graph.compile()

    @property
    @abstractmethod
    def state_schema(self) -> type[BaseModel]:
        '''Define your state schema as a Pydantic model'''
        pass

    def _build_graph(self):
        self.graph.add_node("start", self.start)
        self.graph.add_node("process", self.process)
        self.graph.add_node("decide", self.decide)

        self.graph.add_edge("start", "process")
        self.graph.add_edge("process", "decide")
        self.graph.add_conditional_edges(
            "decide",
            self.check_decision,
            {
                "continue": "process",
                "end": END,
            }
        )

        self.graph.set_entry_point("start")

    @abstractmethod
    def start(self, state: dict) -> dict:
        '''Node: start'''
        pass
    @abstractmethod
    def process(self, state: dict) -> dict:
        '''Node: process'''
        pass
    @abstractmethod
    def decide(self, state: dict) -> dict:
        '''Node: decide'''
        pass

    @abstractmethod
    def check_decision(self, state: dict) -> str:
        '''Condition for decide → continue, end'''
        pass
