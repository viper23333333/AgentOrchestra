# Contributing to AgentOrchestra

First off, thank you for considering contributing to AgentOrchestra! This project thrives on community involvement, and every contribution -- whether it's a bug fix, new feature, documentation improvement, or bug report -- is valuable.

This guide will walk you through the contribution process step by step.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Code Review Process](#code-review-process)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this standard:

- Be respectful and inclusive
- Welcome newcomers and help them grow
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| pnpm | 8+ | Frontend package manager |
| Docker | 24+ | Containerization (optional) |
| Git | 2.40+ | Version control |
| pre-commit | 3.8+ | Git hooks |

### Fork and Clone

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/AgentOrchestra.git
cd AgentOrchestra

# 3. Add the upstream remote
git remote add upstream https://github.com/your-org/AgentOrchestra.git

# 4. Verify remotes
git remote -v
```

---

## Development Environment Setup

### Quick Setup

```bash
# Install all dependencies and pre-commit hooks
make setup
```

### Manual Setup

#### Backend

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev,test]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

#### Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Enable corepack and install dependencies
corepack enable
pnpm install

# Copy environment template
cp .env.local.example .env.local
```

#### Pre-commit Hooks

```bash
# Install pre-commit hooks (from project root)
pre-commit install
pre-commit install --hook-type commit-msg
```

### Verify Setup

```bash
# Run all quality checks
make check

# Or run individually:
make test          # Run tests
make lint          # Run linters
make typecheck     # Type checking
```

---

## Development Workflow

### Branch Naming Convention

We use a branching strategy based on the type of contribution:

| Type | Branch Pattern | Example |
|------|---------------|---------|
| Feature | `feature/<short-description>` | `feature/add-webhook-support` |
| Bug fix | `fix/<short-description>` | `fix/revision-loop-overflow` |
| Documentation | `docs/<short-description>` | `docs/api-authentication` |
| Refactoring | `refactor/<short-description>` | `refactor/llm-adapter-cleanup` |
| Performance | `perf/<short-description>` | `perf/streaming-latency` |
| Chore | `chore/<short-description>` | `chore/update-dependencies` |

### Creating a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create your feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

```bash
# Start backend in development mode (hot-reload)
make dev-backend

# Start frontend in development mode (hot-reload)
make dev-frontend

# Or start both with Docker
make dev
```

### Syncing Your Branch

```bash
# Regularly rebase on upstream/main to avoid conflicts
git fetch upstream
git rebase upstream/main
```

---

## Code Standards

### Python (Backend)

We use **Ruff** for linting and formatting, and **mypy** for type checking.

```bash
# Lint and auto-fix
make lint-backend

# Format code
make format-backend

# Type check
make typecheck-backend
```

**Key Rules:**

- Line length: 100 characters
- Use type hints for all function signatures
- Use `from __future__ import annotations` for forward references
- Docstrings follow Google-style format
- All classes and public methods must have docstrings
- Use `async/await` for I/O-bound operations
- Import order: stdlib, third-party, first-party (enforced by isort via Ruff)

**Example:**

```python
from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MyModel(BaseModel):
    """A brief description of the model.

    More detailed description if needed.

    Attributes:
        name: The name of the entity.
        count: The number of items.
    """

    name: str = Field(..., min_length=1, description="Entity name")
    count: int = Field(default=0, ge=0, description="Item count")

    async def process(self, context: dict[str, Any]) -> str:
        """Process the model with the given context.

        Args:
            context: Additional processing context.

        Returns:
            The processing result string.
        """
        logger.info("Processing %s (count=%d)", self.name, self.count)
        return f"Processed {self.name}"
```

### TypeScript / React (Frontend)

We use **ESLint** and **Prettier** for linting and formatting.

```bash
# Lint
make lint-frontend

# Format
make format-frontend

# Type check
make typecheck-frontend
```

**Key Rules:**

- Use functional components with TypeScript
- Prefer `const` over `let`, never use `var`
- Use named exports for components
- Follow the existing file naming convention (PascalCase for components)
- Keep components small and focused
- Use custom hooks for reusable logic

### General Guidelines

- **Write self-documenting code** -- Code should be readable without comments
- **Keep functions small** -- Each function should do one thing well
- **DRY principle** -- Don't repeat yourself; extract shared logic
- **Error handling** -- Always handle errors gracefully with meaningful messages
- **No hardcoded secrets** -- Use environment variables for all sensitive data
- **Test coverage** -- Write tests for new features and bug fixes

---

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) v1.0.0. This is enforced by `commitlint` via pre-commit hooks.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style changes (formatting, semicolons, etc.) |
| `refactor` | Code refactoring without feature changes |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance tasks |
| `revert` | Revert a previous commit |

### Scopes

| Scope | Description |
|-------|-------------|
| `agents` | Agent-related changes |
| `api` | API endpoint changes |
| `core` | Core orchestration changes |
| `llm` | LLM provider/adapter changes |
| `memory` | Memory/conversation changes |
| `tools` | Agent tools changes |
| `config` | Configuration changes |
| `frontend` | Frontend changes |
| `docker` | Docker/deployment changes |
| `docs` | Documentation changes |

### Examples

```
feat(agents): add custom tool support for coder agent

Implement tool registration system that allows the coder agent
to dynamically discover and use available tools during execution.

Closes #123
```

```
fix(core): prevent infinite loop in revision cycle

The reviewer agent could get stuck in an infinite revision loop
when the code quality threshold was never met. This adds a
hard limit check before routing back to the coder.

Fixes #456
```

```
docs(api): add streaming endpoint examples

Add curl and JavaScript examples for the SSE streaming endpoint
to the API documentation.
```

---

## Pull Request Process

### Before Submitting

1. **Sync with upstream** -- Rebase on the latest `main` branch
2. **Run quality checks** -- Ensure `make check` passes
3. **Write tests** -- Add tests for new features and bug fixes
4. **Update documentation** -- Update relevant docs for any user-facing changes
5. **Update CHANGELOG.md** -- Add an entry under "Unreleased"

### Submitting a PR

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request against the `main` branch on GitHub

3. Fill in the PR template:
   - **Description** -- What does this PR do and why?
   - **Related Issues** -- Link to related issues (e.g., `Closes #123`)
   - **Type of Change** -- Feature, bug fix, breaking change, etc.
   - **Testing** -- How was this tested?
   - **Checklist** -- Confirm all items are complete

### PR Checklist

- [ ] Code compiles and passes all tests (`make check`)
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated (if applicable)
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] No hardcoded secrets or credentials
- [ ] Commit messages follow Conventional Commits
- [ ] PR title follows Conventional Commits format
- [ ] Branch is up to date with `main`

### After Submitting

- A maintainer will review your PR within a few days
- Address review feedback by pushing additional commits to your branch
- Do not force-push or squash commits during review unless asked
- Once approved, a maintainer will merge your PR

---

## Issue Reporting

### Bug Reports

When reporting a bug, please use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

1. **Description** -- Clear description of the bug
2. **Steps to Reproduce** -- Minimal steps to reproduce the issue
3. **Expected Behavior** -- What you expected to happen
4. **Actual Behavior** -- What actually happened
5. **Environment** -- OS, Python version, Node.js version, etc.
6. **Logs** -- Relevant error logs or stack traces
7. **Screenshots** -- If applicable

### Feature Requests

When requesting a feature, please use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

1. **Problem** -- What problem does this solve?
2. **Proposed Solution** -- How should it work?
3. **Alternatives** -- Any alternative solutions considered
4. **Use Case** -- Real-world use case examples

### Good Issue Practices

- **Search first** -- Check if the issue has already been reported
- **One issue per topic** -- Don't combine multiple unrelated issues
- **Be specific** -- Provide as much detail as possible
- **Be patient** -- Maintainers will respond as soon as possible

---

## Code Review Process

### For Contributors

- **Be responsive** -- Address review comments promptly
- **Be open-minded** -- Accept feedback constructively
- **Explain your reasoning** -- If you disagree, explain why politely
- **Keep PRs small** -- Smaller PRs are easier to review and merge

### For Reviewers

- **Be respectful** -- Provide constructive, kind feedback
- **Be thorough** -- Check for bugs, performance issues, and code quality
- **Be timely** -- Review PRs within a reasonable timeframe
- **Focus on the "why"** -- Explain the reasoning behind suggestions
- **Use conventional comments** -- Prefix with `nit:`, `question:`, `suggestion:`, or `issue:`

### Review Labels

| Label | Meaning |
|-------|---------|
| `nit:` | Minor, non-blocking suggestion |
| `question:` | Clarification needed |
| `suggestion:` | Recommended improvement |
| `issue:` | Must be addressed before merging |
| `praise:` | Positive feedback on good code |

---

## Getting Help

If you need help at any point during the contribution process:

- **GitHub Discussions** -- Ask questions and share ideas
- **GitHub Issues** -- Report bugs or request features
- **Documentation** -- Check the [docs/](docs/) directory for detailed guides

Thank you for contributing to AgentOrchestra! Your efforts help make this project better for everyone.
