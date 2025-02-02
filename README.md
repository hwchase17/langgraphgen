# LangGraphGen

1. `pip install -e . langgraph`
2. Define `yaml` file for graph (see `agent_graph.yaml` for an example)
3. Generate agent stub: `langgraph-gen agent_graph.yaml -o generated_agent.py` (this will create `generated_agent.yaml`)
4. Implement agent class (see `my_agent.py` for an example of implemented agent class)

