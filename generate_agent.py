#!/usr/bin/env python3
"""
LangGraph Agent Code Generator CLI
"""

import argparse
import yaml
import jinja2
import sys
from pathlib import Path
from typing import Optional

__version__ = "0.1.0"

TEMPLATE = """\
from abc import ABC, abstractmethod
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class {{ class_name }}(ABC):
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
        {% for node in nodes %}
        self.graph.add_node("{{ node.name }}", self.{{ node.name }})
        {% endfor %}

        {% for edge in edges %}
        {% if edge.condition is defined %}
        self.graph.add_conditional_edges(
            "{{ edge.from }}",
            self.{{ edge.condition }},
            {
                {% for key, value in edge.paths.items() %}
                "{{ key }}": {% if value == 'end' %}END{% else %}"{{ value }}"{% endif %},
                {% endfor %}
            }
        )
        {% else %}
        self.graph.add_edge("{{ edge.from }}", "{{ edge.to }}")
        {% endif %}
        {% endfor %}

        self.graph.set_entry_point("{{ entrypoint }}")

    {% for node in nodes %}
    @abstractmethod
    def {{ node.name }}(self, state: dict) -> dict:
        '''Node: {{ node.name }}'''
        pass
    {% endfor %}

    {% for edge in edges if edge.condition is defined %}
    @abstractmethod
    def {{ edge.condition }}(self, state: dict) -> str:
        '''Condition for {{ edge.from }} → {{ edge.paths|join(', ') }}'''
        pass
    {% endfor %}
"""

def validate_spec(spec: dict) -> bool:
    required_fields = {"entrypoint", "nodes", "edges"}
    if not required_fields.issubset(spec.keys()):
        missing = required_fields - spec.keys()
        raise ValueError(f"Missing required fields in spec: {', '.join(missing)}")
    
    node_names = {n["name"] for n in spec["nodes"]}
    for edge in spec["edges"]:
        if edge["from"] not in node_names:
            raise ValueError(f"Edge source node '{edge['from']}' not defined in nodes")
        if "to" in edge and edge["to"] not in node_names:
            raise ValueError(f"Edge target node '{edge['to']}' not defined in nodes")
    return True

def generate_agent(
    input_file: Path,
    output_file: Optional[Path],
    class_name: str = "GeneratedAgent"
) -> None:
    try:
        spec = yaml.safe_load(input_file.read_text())
        validate_spec(spec)
    except Exception as e:
        sys.exit(f"Error loading spec: {str(e)}")

    env = jinja2.Environment(loader=jinja2.BaseLoader, trim_blocks=True, lstrip_blocks=True)
    
    try:
        template = env.from_string(TEMPLATE)
        code = template.render(
            class_name=class_name,
            nodes=spec["nodes"],
            edges=spec["edges"],
            entrypoint=spec["entrypoint"]
        )
    except jinja2.TemplateError as e:
        sys.exit(f"Template error: {str(e)}")

    output_path = output_file or input_file.with_suffix(".py")
    output_path.write_text(code)
    print(f"Successfully generated agent code in {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate LangGraph agent base classes from YAML specs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input YAML specification file"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output Python file path",
        default=None
    )
    parser.add_argument(
        "-n", "--class-name",
        type=str,
        default="GeneratedAgent",
        help="Name for the generated base class"
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"Input file {args.input} does not exist")

    generate_agent(
        input_file=args.input,
        output_file=args.output,
        class_name=args.class_name
    )

if __name__ == "__main__":
    main()
