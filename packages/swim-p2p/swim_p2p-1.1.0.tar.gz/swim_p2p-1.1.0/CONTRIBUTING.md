# Contributing to SWIM P2P

Thanks for your interest in contributing! This guide will help you get started.

## Quick Start

### Setup

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/yourusername/swim_p2p.git
cd swim_p2p

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

## Making Changes

```shellscript
git checkout -b your-branch-name
# Make your changes
pytest  # Run tests
git commit -m "describe your change"
git push origin your-branch-name
```

Then create a pull request.

## Guidelines

- Follow existing code style
- Add tests for new features
- Keep commits focused and descriptive
- Be respectful in discussions

## Need Help?

Open an issue or discussion on GitHub.