from setuptools import setup

setup(
    name="langgraph-gen",
    version="0.1.0",
    py_modules=["generate_agent"],
    install_requires=["pyyaml", "jinja2"],
    entry_points={
        "console_scripts": ["langgraph-gen=generate_agent:main"]
    }
)