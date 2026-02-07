# Contributing to TriLLM Arena

Thank you for your interest in contributing to TriLLM Arena! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Help others learn and grow
- Report issues responsibly

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/trillm-arena.git
cd trillm-arena
```

### 2. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-fix
```

### 3. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt
pip install pylint black flake8 mypy pytest

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Development Workflow

### Code Style

We follow these standards:

- **Format**: Black (run `black trillm_arena/`)
- **Lint**: Flake8 (run `flake8 trillm_arena/`)
- **Type Hints**: MyPy (run `mypy trillm_arena/`)
- **Docstrings**: Google style with type hints

### Before Committing

```bash
# Format code
black trillm_arena/

# Check linting
flake8 trillm_arena/

# Type checking
mypy trillm_arena/ --ignore-missing-imports

# Run tests
pytest tests/ -v
```

### Commit Messages

Follow conventional commits:

```
feat: add new feature
fix: fix a bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

Example:
```
feat: add GPU support for faster inference

- Add docker-compose.gpu.yml
- Update documentation with GPU setup
- Add CUDA configuration
```

## Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Update docstrings in modified code
   - Add entry to CHANGELOG.md

2. **Add Tests**
   - Add unit tests for new features
   - Ensure existing tests pass
   - Aim for >80% code coverage

3. **Run Quality Checks**
   ```bash
   black trillm_arena/
   flake8 trillm_arena/
   mypy trillm_arena/ --ignore-missing-imports
   pytest tests/ -v
   ```

4. **Create Pull Request**
   - Provide descriptive title
   - Include motivation and context
   - Link related issues
   - Add screenshots for UI changes

5. **Review Process**
   - Respond to reviewer comments
   - Make requested changes
   - Re-request review after updates

## Reporting Issues

### Bug Reports

Include:
- [ ] Clear description of the bug
- [ ] Steps to reproduce
- [ ] Expected behavior
- [ ] Actual behavior
- [ ] Python version
- [ ] Docker version (if applicable)
- [ ] Error messages/logs
- [ ] Screenshots (if applicable)

Template:
```markdown
**Describe the bug:**
A clear description of what the bug is.

**Steps to reproduce:**
1. ...
2. ...

**Expected behavior:**
What should happen.

**Actual behavior:**
What actually happens.

**Environment:**
- Python version: 3.11
- Docker version: 24.0
- OS: Ubuntu 22.04

**Logs:**
```
Error message here
```
```

### Feature Requests

Include:
- [ ] Clear description of the feature
- [ ] Motivation (why do you need it?)
- [ ] Example use cases
- [ ] Suggested implementation (optional)

## Areas for Contribution

### High Priority
- [ ] Database integration for debate history
- [ ] Performance optimizations
- [ ] Additional model support
- [ ] Enhanced error messages

### Medium Priority
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Custom judge models
- [ ] Debate export formats

### Low Priority
- [ ] UI improvements
- [ ] Documentation improvements
- [ ] Example notebooks
- [ ] Additional testing

## Development Tips

### Local Testing

```bash
# Run locally without Docker
pip install -r requirements.txt
ollama pull mistral llama3 mixtral

# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start API
uvicorn trillm_arena.api:app --reload

# Terminal 3: Start UI
streamlit run trillm_arena/app.py
```

### Docker Testing

```bash
# Build custom image
docker build -t trillm-arena:dev .

# Test with docker-compose
docker-compose up -d
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_debate_engine.py -v

# Run with coverage
pytest tests/ --cov=trillm_arena --cov-report=html
```

## Documentation Style

### Docstring Template

```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Longer description if needed. Explain what it does,
    any side effects, and important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input provided
        CustomError: When custom condition occurs
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
    """
```

## Release Process

### For Maintainers

1. Update CHANGELOG.md
2. Update version in `__init__.py`
3. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will automatically create release

## Questions?

- Check existing [Issues](https://github.com/soumyadarshandash/trillm-arena/issues)
- Check [Discussions](https://github.com/soumyadarshandash/trillm-arena/discussions)
- Read [Documentation](README.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to TriLLM Arena! 🚀**

Your contributions make this project better for everyone!
