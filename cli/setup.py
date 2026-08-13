from setuptools import setup, find_packages

setup(
    name="askill",
    version="1.0.0",
    description="Lightweight Agentic Skill Vault CLI & Smart Search Engine for Autonomous AI Agents",
    author="Unified Agentic Skill Manager Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "askill=askill.cli:main",
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
