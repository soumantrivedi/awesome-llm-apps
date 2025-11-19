# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the FuturisticPM multi-agent system.

## ADR Index

### [ADR-001: High Level Solution Architecture](./ADR-001-high-level-solution-architecture.md)
**Status**: Accepted  
**Summary**: Defines the overall layered microservices architecture with presentation, orchestration, agent, integration, and data layers.

**Key Decisions**:
- Layered microservices architecture
- Event-driven communication
- Kubernetes for orchestration
- PostgreSQL for production data

---

### [ADR-002: Best Platform for Agent Hosting](./ADR-002-best-platform-for-agent-hosting.md)
**Status**: Accepted  
**Summary**: Selects Kubernetes (EKS/GKE/AKS) as the primary hosting platform for AI agents with hybrid strategy.

**Key Decisions**:
- Kubernetes for stateful agents
- Managed containers (Fargate/Cloud Run) for stateless agents
- Horizontal Pod Autoscaler (HPA) for scaling
- Persistent volumes for agent memory

---

### [ADR-003: User Authentication and Authorization](./ADR-003-user-authentication-authorization.md)
**Status**: Accepted  
**Summary**: Implements OAuth 2.0/OIDC-based authentication with enterprise SSO and RBAC.

**Key Decisions**:
- OAuth 2.0 / OIDC with enterprise SSO
- Role-based access control (RBAC)
- Multi-tenant isolation
- JWT tokens with refresh tokens
- API keys for integrations

---

### [ADR-004: Architecture Pattern for Core PM Agents](./ADR-004-architecture-pattern-core-pm-agents.md)
**Status**: Accepted  
**Summary**: Defines Stateful Agent Pattern for 6 core PM agents (Strategy, Research, Roadmap, Metrics, Stakeholder, Execution).

**Key Decisions**:
- Stateful agent pattern with state manager
- Sequential workflow execution
- Context passing between agents
- Structured output processing
- State persistence with versioning

---

### [ADR-005: Architecture Pattern for Integration Agents](./ADR-005-architecture-pattern-integration-agents.md)
**Status**: Accepted  
**Summary**: Defines Adapter Pattern with Circuit Breaker for 4 integration agents (Jira, Confluence, GitHub, Slack).

**Key Decisions**:
- MCP protocol as primary integration method
- Direct API fallback
- Circuit breaker pattern
- Rate limiting per service
- OAuth 2.0 token management

---

### [ADR-006: Architecture Pattern for Specialized Agents](./ADR-006-architecture-pattern-specialized-agents.md)
**Status**: Accepted  
**Summary**: Defines Learning Agent Pattern with Memory System for 2 specialized agents (Self-Evolving, Agile Coach).

**Key Decisions**:
- Vector database for semantic memory
- Learning engine with feedback processing
- Reflection module for self-improvement
- Knowledge base for domain expertise
- RAG pattern for knowledge retrieval

---

### [ADR-007: Agent-to-Agent Interaction Pattern](./ADR-007-agent-to-agent-interaction-pattern.md)
**Status**: Accepted  
**Summary**: Defines Orchestrator Pattern with Event-Driven Communication for agent coordination.

**Key Decisions**:
- Central orchestrator with coordination rules
- Event bus (Redis Streams) for async communication
- Support for sequential, parallel, and conditional patterns
- Context manager for state sharing
- Agent registry for service discovery

---

## ADR Format

Each ADR follows this structure:
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: Background and situation
- **Problem Statement**: What problem are we solving?
- **Decision**: What decision was made?
- **Solution Options**: Alternatives considered
- **Functional Requirements**: What the solution must do
- **Non-Functional Requirements**: Quality attributes
- **Consequences**: Positive and negative impacts
- **Implementation Notes**: Technical details

## Decision Timeline

| Date | ADR | Decision |
|------|-----|----------|
| 2025-11 | ADR-001 | High-level architecture: Layered microservices |
| 2025-11 | ADR-002 | Agent hosting: Kubernetes |
| 2025-11 | ADR-003 | Auth/Authz: OAuth 2.0/OIDC with SSO |
| 2025-11 | ADR-004 | Core PM agents: Stateful pattern |
| 2025-11 | ADR-005 | Integration agents: Adapter pattern |
| 2025-11 | ADR-006 | Specialized agents: Learning pattern |
| 2025-11 | ADR-007 | Agent interaction: Orchestrator pattern |

## Related Documentation

- [Main README](../README.md) - Project overview
- [Requirements](../../../../requirements/Additional-Requirements.md) - Agent responsibilities
- [AgenticPM Journey](../../../../requirements/AgenticPMJourney.pdf) - Product management journey

## Contributing

When creating a new ADR:
1. Use the template format
2. Number sequentially (ADR-008, ADR-009, etc.)
3. Include mermaid diagrams where helpful
4. Reference related ADRs
5. Update this index

