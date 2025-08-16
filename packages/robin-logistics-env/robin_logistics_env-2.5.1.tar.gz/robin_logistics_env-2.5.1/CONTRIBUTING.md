# Contributing to Robin Logistics Environment

Thank you for your interest in contributing! This project welcomes contributions from the community.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature/fix
4. **Make changes** and test them
5. **Submit a pull request**

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/robin-logistics-env.git
cd robin-logistics-env

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8

# Run tests
python -m pytest tests/
```

## 🎯 Areas for Contribution

### **High Priority**
- **New solver algorithms** in `examples/`
- **Performance optimizations** in distance/pathfinding
- **Additional test scenarios** in `tests/`
- **Documentation improvements**

### **Medium Priority**
- **Dashboard enhancements** (new visualizations)
- **Configuration options** (new scenario types)
- **CLI improvements** (new flags/options)

### **Low Priority**
- **Code cleanup** (type hints, docstrings)
- **Example refinements**

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific component
python -m pytest tests/test_environment_mock.py

# Test contestant workflow
cd contestant_example && python test_my_solver.py
```

## 📝 Code Style

- **Follow existing patterns** in the codebase
- **Keep docstrings** minimal but clear [[memory:5817585]]
- **No excessive print statements** or emojis in code [[memory:5267876]]
- **Professional tone** in comments and outputs [[memory:5267876]]

## 🔍 Pull Request Guidelines

### **Before Submitting**
- [ ] Code follows existing style
- [ ] Tests pass: `python -m pytest tests/`
- [ ] Contestant example works: `cd contestant_example && python test_my_solver.py`
- [ ] Documentation updated if needed

### **PR Description Template**
```markdown
## Changes
- Brief description of what changed

## Testing
- How you tested the changes
- Any new test cases added

## Impact
- Does this affect contestant API? (Yes/No)
- Does this change existing behavior? (Yes/No)
```

## 🐛 Bug Reports

Please include:
- **Environment details** (Python version, OS)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Code sample** if possible

## 💡 Feature Requests

Please describe:
- **Use case** - what problem does this solve?
- **Proposed solution** - how should it work?
- **Alternatives considered** - other approaches?

## 📧 Questions

- **Issues** for bugs and feature requests
- **Discussions** for general questions
- **Email**: mario.salama@beltoneholding.com for sensitive matters

## 🏆 Recognition

Contributors will be:
- **Listed** in releases and changelog
- **Credited** in documentation
- **Thanked** publicly for their contributions

---

**Every contribution helps make logistics optimization more accessible!**
