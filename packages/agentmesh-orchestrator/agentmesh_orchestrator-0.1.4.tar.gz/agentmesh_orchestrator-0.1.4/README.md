# AgentMesh

A production-grade multi-agent orchestration platform built on Microsoft AutoGen, enabling sophisticated agent collaboration through mesh networking with CLI and REST API interfaces.

## Features

### 🤖 Multi-Agent Orchestration
- **Sequential**: Linear workflows where agents build on each other's work
- **Round-Robin**: Collaborative discussions with turn-based participation
- **Graph-Based**: Complex workflows with conditional branching and parallel execution
- **Swarm Coordination**: Autonomous agent collaboration with self-organizing behavior

### 🔧 Flexible Communication
- Message passing with context preservation
- Agent handoff mechanisms with specialization routing
- Real-time monitoring and analytics
- Parameter tuning during execution

### 💻 Dual Interface
- **CLI Tool**: Complete command-line interface for workflow management
- **REST API**: Full-featured API with OpenAPI documentation
- **Configuration**: YAML-based workflow definitions with validation

### 🚀 Production Ready
- Real-time monitoring and metrics
- Performance optimization and caching
- Comprehensive logging and debugging
- Scalable architecture with AutoGen native integration

### 📊 Advanced Features
- Graph visualization (ASCII, Mermaid, JSON)
- Swarm analytics and handoff pattern analysis
- Runtime parameter tuning
- Quality gates and conditional routing
- Parallel execution and synchronization

## Quick Start

### Installation

```bash
# Install with Poetry (recommended)
poetry install

# Or with pip
pip install -e .
```

### Basic Usage

#### CLI Interface

```bash
# Create agents
agentmesh agent create --name "architect" --type "assistant" --model "gpt-4o"
agentmesh agent create --name "developer" --type "assistant" --model "gpt-4o"

# List agents
agentmesh agent list

# Create and run a workflow
agentmesh workflow create --config examples/code-review-workflow.yaml
agentmesh workflow run --id workflow-123 --task "Build a REST API for user management"
```

#### API Interface

```bash
# Start the API server
agentmesh server start --port 8000

# Create agent via API
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "architect",
    "type": "assistant",
    "model": "gpt-4o",
    "system_message": "You are a software architect"
  }'
```

## Orchestration Patterns & Examples

AutoGen A2A supports four distinct orchestration patterns, each optimized for different collaboration scenarios:

### 1. Sequential Orchestration
**Use Case**: Linear workflows where each agent builds on the previous agent's work.

```yaml
# examples/workflows/sequential-code-review.yaml
name: "Code Review Pipeline"
pattern: "sequential"

agents:
  - name: "developer"
    type: "assistant"
    system_message: "You write clean, well-documented code"
  - name: "reviewer"
    type: "assistant"
    system_message: "You review code for best practices and bugs"
  - name: "architect"
    type: "assistant"
    system_message: "You ensure architectural compliance"

execution:
  max_rounds: 3
  timeout: 1800
```

```bash
# Run sequential workflow
agentmesh workflow create --config sequential-code-review.yaml
agentmesh workflow execute workflow-123 --task "Implement user authentication API"
```

### 2. Round-Robin Orchestration
**Use Case**: Collaborative discussions where agents take turns contributing ideas.

```yaml
# examples/workflows/round-robin-brainstorm.yaml
name: "Product Brainstorming Session"
pattern: "round_robin"

agents:
  - name: "product_manager"
    type: "assistant"
    system_message: "You focus on user needs and business value"
  - name: "designer"
    type: "assistant"
    system_message: "You consider user experience and interface design"
  - name: "engineer"
    type: "assistant"
    system_message: "You evaluate technical feasibility"

termination:
  type: "max_messages"
  value: 12

execution:
  max_rounds: 4
  timeout: 2400
```

```bash
# Run round-robin workflow
agentmesh workflow create --config round-robin-brainstorm.yaml
agentmesh workflow execute workflow-123 --task "Design a mobile app for food delivery"
```

### 3. Graph-Based Orchestration
**Use Case**: Complex workflows with conditional branching, parallel execution, and quality gates.

```yaml
# examples/workflows/graph-product-development.yaml
name: "Product Development Pipeline"
pattern: "graph"

agents:
  - name: "product_manager"
    type: "assistant"
  - name: "designer"
    type: "assistant"
  - name: "frontend_dev"
    type: "assistant"
  - name: "backend_dev"
    type: "assistant"
  - name: "qa_engineer"
    type: "assistant"

graph:
  nodes:
    - id: "requirements"
      agent: "product_manager"
      description: "Define product requirements"
    - id: "design"
      agent: "designer"
      description: "Create UI/UX designs"
    - id: "frontend"
      agent: "frontend_dev"
      description: "Implement frontend"
    - id: "backend"
      agent: "backend_dev"
      description: "Implement backend"
    - id: "testing"
      agent: "qa_engineer"
      description: "Test and validate"
  
  edges:
    - id: "req_to_design"
      source: "requirements"
      target: "design"
      type: "sequential"
    - id: "design_to_frontend"
      source: "design"
      target: "frontend"
      type: "parallel"
    - id: "design_to_backend"
      source: "design"
      target: "backend"
      type: "parallel"
    - id: "frontend_to_testing"
      source: "frontend"
      target: "testing"
      type: "synchronize"
    - id: "backend_to_testing"
      source: "backend"
      target: "testing"
      type: "synchronize"
  
  conditions:
    quality_gate:
      type: "evaluation"
      criteria: ["code_quality", "test_coverage"]
```

```bash
# Run graph workflow with visualization
agentmesh workflow create --config graph-product-development.yaml
agentmesh workflow visualize workflow-123 --format mermaid
agentmesh workflow execute workflow-123 --task "Build an e-commerce checkout system"
```

### 4. Swarm Coordination
**Use Case**: Autonomous agent collaboration with self-organizing behavior and dynamic handoffs.

```yaml
# examples/workflows/swarm-research-analysis.yaml
name: "Research Analysis Swarm"
pattern: "swarm"

agents:
  - name: "data_collector"
    type: "assistant"
    system_message: "You excel at gathering research data from multiple sources"
  - name: "analyst"
    type: "assistant"
    system_message: "You analyze data and identify patterns and insights"
  - name: "statistician"
    type: "assistant"
    system_message: "You perform statistical analysis and validation"
  - name: "report_generator"
    type: "assistant"
    system_message: "You create comprehensive research reports"

swarm:
  participants:
    - agent_id: "data_collector"
      specializations: ["data_collection", "web_scraping", "research"]
      handoff_targets: ["analyst", "statistician"]
      participation_weight: 1.2
      max_consecutive_turns: 3
    
    - agent_id: "analyst"
      specializations: ["data_analysis", "pattern_recognition", "insights"]
      handoff_targets: ["statistician", "report_generator"]
      participation_weight: 1.0
      max_consecutive_turns: 4
    
    - agent_id: "statistician"
      specializations: ["statistics", "validation", "hypothesis_testing"]
      handoff_targets: ["analyst", "report_generator"]
      participation_weight: 0.8
      max_consecutive_turns: 2
    
    - agent_id: "report_generator"
      specializations: ["writing", "reporting", "documentation"]
      handoff_targets: ["analyst"]
      participation_weight: 1.0
      max_consecutive_turns: 3

  termination:
    max_messages: 25
    timeout_seconds: 1800

  handoff_config:
    autonomous_threshold: 0.7
    broadcast_threshold: 0.3
    load_balancing: true
```

```bash
# Run swarm workflow with monitoring
agentmesh swarm create --config swarm-research-analysis.yaml
agentmesh swarm monitor --id swarm-123 --metrics all --refresh 5
agentmesh swarm tune --id swarm-123 --parameter participation_balance --value 0.8
agentmesh swarm analytics --id swarm-123 --output json
```

### Pattern Comparison

| Pattern | Best For | Complexity | Control | Autonomy |
|---------|----------|------------|---------|----------|
| **Sequential** | Linear workflows, step-by-step processes | Low | High | Low |
| **Round-Robin** | Collaborative discussions, brainstorming | Low | Medium | Low |
| **Graph** | Complex workflows, conditional logic | High | High | Medium |
| **Swarm** | Dynamic collaboration, emergent behavior | Medium | Medium | High |

### Advanced Examples

For complete examples with full configurations, see the `examples/workflows/` directory:

- **Sequential**: `sequential-document-processing.yaml`, `sequential-data-pipeline.yaml`
- **Round-Robin**: `round-robin-creative-writing.yaml`, `round-robin-problem-solving.yaml`
- **Graph**: `graph-code-review.yaml`, `graph-content-creation-pipeline.yaml`, `graph-advanced-product-development.yaml`
- **Swarm**: `swarm-product-development.yaml`, `swarm-content-creation.yaml`, `swarm-financial-analysis.yaml`

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [CLI Reference](docs/cli-reference.md)
- [Orchestration Patterns](docs/orchestration-patterns.md)
- [Graph Workflows](docs/graph-workflows.md)
- [Swarm Coordination](docs/swarm-coordination.md)
- [Examples](examples/)

### Pattern-Specific Guides

- **Sequential & Round-Robin**: Built-in patterns for linear and collaborative workflows
- **[Graph Workflows](docs/graph-workflows.md)**: Complex workflows with conditional branching, parallel execution, and quality gates
- **[Swarm Coordination](docs/swarm-coordination.md)**: Autonomous agent collaboration with self-organizing behavior

### CLI Quick Reference

```bash
# Workflow Management
agentmesh workflow create --config config.yaml
agentmesh workflow list --status running
agentmesh workflow execute workflow-123 --task "Your task here"
agentmesh workflow get workflow-123 --format json

# Graph Workflows
agentmesh workflow visualize workflow-123 --format mermaid
agentmesh workflow pause workflow-123
agentmesh workflow resume workflow-123

# Swarm Coordination
agentmesh swarm create --config swarm-config.yaml
agentmesh swarm monitor --id swarm-123 --metrics all
agentmesh swarm tune --id swarm-123 --parameter participation_balance --value 0.8
agentmesh swarm analytics --id swarm-123 --output json

# Agent Management
agentmesh agent create --name "agent" --type "assistant" --model "gpt-4o"
agentmesh agent list --format table
```

## Development

### Prerequisites

- Python 3.11+
- Poetry
- Redis (for message queuing)
- PostgreSQL (for persistence)

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd autogen-agent

# Install dependencies
poetry install

# Setup pre-commit hooks
poetry run pre-commit install

# Start development services
docker-compose up -d redis postgres

# Run tests
poetry run pytest

# Start development server
poetry run agentmesh server start --reload
```

### Project Structure

```
agentmesh/
├── src/
│   └── agentmesh/
│       ├── api/           # FastAPI application
│       ├── cli/           # CLI commands
│       ├── core/          # Core agent logic
│       ├── models/        # Data models
│       ├── services/      # Business logic
│       └── utils/         # Utilities
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example workflows
└── deployment/            # Deployment configs
```

## Implementation Status

This project is currently under active development following the [Sprint Planning Document](SPRINT-PLANNING.md).

### ✅ Completed Sprints

- **Sprint 1**: Core Foundation & CLI Bootstrap 
- **Sprint 2**: REST API Foundation & Agent Registry
- **Sprint 3**: Message Infrastructure & Communication
- **Sprint 4**: Security, Monitoring & Handoff Management
- **Sprint 5**: Sequential & Round-Robin Orchestration
- **Sprint 6**: Graph-based Workflows
- **Sprint 7**: Swarm Coordination

### 🔄 Current Focus: Sprint 8 - Performance Optimization & Caching

**System Status**: Production-ready for orchestration patterns, monitoring, and CLI/API interfaces.

### Key Features Available:

- ✅ **Multi-Agent Orchestration**: All four patterns (Sequential, Round-Robin, Graph, Swarm)
- ✅ **CLI Interface**: Complete command-line tool with workflow management
- ✅ **REST API**: Full API with OpenAPI documentation
- ✅ **Monitoring**: Real-time metrics, analytics, and visualization
- ✅ **Configuration**: YAML-based workflow definitions with validation
- ✅ **Examples**: Comprehensive examples for all orchestration patterns

See the full [implementation roadmap](SPRINT-PLANNING.md) for detailed progress tracking.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Microsoft AutoGen](https://github.com/microsoft/autogen)
- [AutoGen Studio](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-studio)
- [AutoGen Core](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-core)
