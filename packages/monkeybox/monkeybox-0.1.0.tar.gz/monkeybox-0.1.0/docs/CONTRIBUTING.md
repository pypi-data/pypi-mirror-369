# Contributing to Monkeybox

This guide covers development workflow, code quality standards, and contribution guidelines for the Monkeybox framework.

## Development Workflow

### Code Quality Tools
- **Ruff**: Linting and formatting
  ```bash
  uv run ruff check . --fix
  uv run ruff format .
  ```
- **ty**: Type checking
  ```bash
  uv run ty check src/monkeybox
  ```
- **pytest-cov**: Coverage testing
  ```bash
  uv run pytest --cov=src/monkeybox --cov-fail-under=90
  ```
- **Pre-commit hooks**: Automatically run on commit including coverage check
  ```bash
  uv run pre-commit
  ```

### Quality Standards
- **Code Coverage**: Minimum 90% enforced by pre-commit hooks
- **Linting**: Ruff configuration with 100-character line length
- **Type Checking**: Enabled via ty with strict settings
- **Testing**: Comprehensive test suite with extensive coverage
- **Self Documenting Code**: Prefer self documenting code over excessive comments

### Package Management
- **Always use `uv`** - never pip directly
- Add dependencies: `uv add package-name`
- Sync environment: `uv sync`

## Testing Standards

All new features must include comprehensive unit tests:
- Mock external dependencies to keep tests fast
- Follow existing test patterns in the `tests/` directory
- Ensure tests are clear, focused, and maintainable
- Target 90%+ coverage for new code
- Include edge cases and error scenarios
- Document complex tests with detailed docstrings
- Run full test suite before committing

## Development Process

1. **Test-Driven Development**: Write tests first, then implement features
2. **Coverage Requirements**: Maintain 90%+ test coverage (enforced by pre-commit)
3. **Code Quality**: Follow existing patterns and use provided tools (ruff, ty)
4. **Documentation**: Update CLAUDE.md and relevant docs for any feature additions or changes

## Pull Request Checklist

- [ ] Tests written and passing (90%+ coverage)
- [ ] Code formatted with ruff
- [ ] Type checking passes with ty
- [ ] Documentation updated with any changes
- [ ] Pre-commit hooks passing

## Architecture Principles

- **Minimal Abstraction**: Don't over-engineer solutions
- **Provider Agnostic**: Support multiple LLM providers equally
- **Observable**: Rich logging for debugging and monitoring
- **Async-First**: Use async/await throughout for performance

## For AI Agents Working on This Codebase

### Documentation Maintenance
**CRITICAL**: When you modify any part of this codebase, you MUST update the CLAUDE.md file and relevant documentation to reflect your changes. This is essential for maintaining accuracy for future AI agents.

**Required Updates Include**:
- New features or components added to the framework
- Changes to existing API interfaces or method signatures
- Updates to testing procedures or coverage requirements
- New development commands or workflow changes
- Architecture modifications or design pattern updates
- Performance optimizations or breaking changes

### AI Agent Development Guidelines

1. **Follow Existing Patterns**: Study the codebase before making changes
2. **Maintain Test Coverage**: Never drop below 90% coverage
3. **Update Documentation**: Keep CLAUDE.md and other docs current
4. **Use Provided Tools**: Always run ruff, ty, and tests before committing
5. **Respect Architecture**: Don't add unnecessary abstractions
