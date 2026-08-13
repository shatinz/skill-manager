from setuptools import setup, find_packages

setup(
    name="eshkill",
    version="1.1.0",
    description="The npm / apt for AI Agent Skills — Autonomous Skill Router, MCP Server, and Smart Search Engine",
    author="Unified Agentic Skill Manager Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "eshkill=eshkill.cli:main",
            "askill=eshkill.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
