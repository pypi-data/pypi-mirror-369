<div align="center">

# AgentScope Runtime

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/agentscope-ai/agentscope-runtime)
[![License](https://img.shields.io/badge/license-Apache%202.0-yellow.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[[中文README]](README_zh.md)

**A Production-Ready Runtime Framework for Intelligent Agent Applications**

*AgentScope Runtime tackles two critical challenges in agent development: secure sandboxed tool execution and scalable agent deployment. Built with a dual-core architecture, it provides framework-agnostic infrastructure for deploying agents with full observability and safe tool interactions.*

</div>

---

## ✨ Key Features

- **🏗️ Deployment Infrastructure**: Built-in services for session management, memory, and sandbox environment control
- **🔒 Sandboxed Tool Execution**: Isolated sandboxes ensure safe tool execution without system compromise

- **🔧 Framework Agnostic**: Not tied to any specific framework. Works seamlessly with popular open-source agent frameworks and custom implementations

- ⚡ **Developer Friendly**: Simple deployment with powerful customization options

- **📊 Observability**: Comprehensive tracing and monitoring for runtime operations

---

## 💬 Contact

Welcome to join our community on

| [Discord](https://discord.gg/eYMpfnkG8h)                     | DingTalk                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| <img src="https://gw.alicdn.com/imgextra/i1/O1CN01hhD1mu1Dd3BWVUvxN_!!6000000000238-2-tps-400-400.png" width="100" height="100"> | <img src="https://img.alicdn.com/imgextra/i1/O1CN01LxzZha1thpIN2cc2E_!!6000000005934-2-tps-497-477.png" width="100" height="100"> |

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📚 Cookbook](#-cookbook)
- [🔌Agent Framework Integration](#-agent-framework-integration)
- [🏗️ Deployment](#️-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip or uv package manager

### Installation

```bash
# Install dependencies
pip install agentscope-runtime

# Install sandbox dependencies
pip install "agentscope-runtime[sandbox]"
```

### Basic Agent Usage Example

This example demonstrates how to create a simple LLM agent using AgentScope Runtime and stream responses from the Qwen model.

```python
import asyncio
import os
from agentscope_runtime.engine import Runner
from agentscope_runtime.engine.agents.llm_agent import LLMAgent
from agentscope_runtime.engine.llms import QwenLLM
from agentscope_runtime.engine.schemas.agent_schemas import AgentRequest
from agentscope_runtime.engine.services.context_manager import ContextManager


async def main():
    # Set up the language model and agent
    model = QwenLLM(
        model_name="qwen-turbo",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    llm_agent = LLMAgent(model=model, name="llm_agent")

    async with ContextManager() as context_manager:
        runner = Runner(agent=llm_agent, context_manager=context_manager)

        # Create a request and stream the response
        request = AgentRequest(
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the capital of France?",
                        },
                    ],
                },
            ],
        )

        async for message in runner.stream_query(request=request):
            if hasattr(message, "text"):
                print(f"Streamed Answer: {message.text}")


asyncio.run(main())
```

### Basic Sandbox Usage Example

This example demonstrates how to create sandboxed and execute tool within the sandbox.

```python
from agentscope_runtime.sandbox import BaseSandbox

with BaseSandbox() as box:
    print(box.run_ipython_cell(code="print('hi')"))
    print(box.run_shell_command(command="echo hello"))
```

---

## 📚 Cookbook

- **[📖 Cookbook](/cookbook/en/intro.md)**: Comprehensive tutorials
- **[💡 Concept](/cookbook/en/concept.md)**: Core concepts and architecture overview
- **[🚀 Quick Start](/cookbook/en/quickstart.md)**: Quick start tutorial
- **[🏠 Demo House](/cookbook/en/demohouse.md)**: Rich example projects

---

## 🔌 Agent Framework Integration

### AgentScope Integration

```python
import os

from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope_runtime.engine.agents.agentscope_agent import AgentScopeAgent

agent = AgentScopeAgent(
    name="Friday",
    model=OpenAIChatModel(
        "gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    agent_config={
        "sys_prompt": "You're a helpful assistant named {name}.",
    },
    agent_builder=ReActAgent,
)
```

### Agno Integration

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agentscope_runtime.engine.agents.agno_agent import AgnoAgent

agent = AgnoAgent(
    name="Friday",
    model=OpenAIChat(
        id="gpt-4",
    ),
    agent_config={
        "instructions": "You're a helpful assistant.",
    },
    agent_builder=Agent,
)
```

### LangGraph Integration

```python
from typing import TypedDict
from langgraph import graph, types
from agentscope_runtime.engine.agents.langgraph_agent import LangGraphAgent


# define the state
class State(TypedDict, total=False):
    id: str


# define the node functions
async def set_id(state: State):
    new_id = state.get("id")
    assert new_id is not None, "must set ID"
    return types.Command(update=State(id=new_id), goto="REVERSE_ID")


async def reverse_id(state: State):
    new_id = state.get("id")
    assert new_id is not None, "ID must be set before reversing"
    return types.Command(update=State(id=new_id[::-1]))


state_graph = graph.StateGraph(state_schema=State)
state_graph.add_node("SET_ID", set_id)
state_graph.add_node("REVERSE_ID", reverse_id)
state_graph.set_entry_point("SET_ID")
compiled_graph = state_graph.compile(name="ID Reversal")
agent = LangGraphAgent(graph=compiled_graph)
```

> [!NOTE]
>
> More agent framework interations are comming soon!

---

## 🏗️ Deployment

The agent runner exposes a `deploy` method that takes a `DeployManager` instance and deploys the agent. The service port is set as the parameter `port` when creating the `LocalDeployManager`. The service endpoint path is set as the parameter `endpoint_path` when deploying the agent. In this example, we set the endpoint path to `/process`. After deployment, you can access the service at `http://localhost:8090/process`.

```python
from agentscope_runtime.engine.deployers import LocalDeployManager

# Create deployment manager
deploy_manager = LocalDeployManager(
    host="localhost",
    port=8090,
)

# Deploy the agent as a streaming service
deploy_result = await runner.deploy(
    deploy_manager=deploy_manager,
    endpoint_path="/process",
    stream=True,  # Enable streaming responses
)
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### 🐛 Bug Reports
- Use GitHub Issues to report bugs
- Include detailed reproduction steps
- Provide system information and logs

### 💡 Feature Requests
- Discuss new ideas in GitHub Discussions
- Follow the feature request template
- Consider implementation feasibility

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For detailed contributing guidelines, please see  [CONTRIBUTE](cookbook/en/contribute.md).

---

## 📄 License

AgentScope Runtime is released under the [Apache License 2.0](LICENSE).

```
Copyright 2025 Tongyi Lab

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
