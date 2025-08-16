# Development and Testing Dependencies

## requirements_dev.txt
- This file lists dependencies needed for development and testing only.
- It keeps development/testing dependencies separate from production requirements.
- Example: Testing frameworks, linters, mock libraries.

## requirements.txt
- This file lists the dependencies required to run the project in production.
- Contains only the packages necessary for deployment.

---

# Difference Between requirements_dev.txt and requirements.txt
- **requirements.txt** → For production environment dependencies.
- **requirements_dev.txt** → For development & testing environment dependencies.

---

# tox.ini
- Used for testing the Python package against different Python versions.
- Tox automates:
  1. Creating virtual environments for different Python versions.
  2. Installing required dependencies.
  3. Running predefined test commands.
- Think of it as a combination of **virtualenvwrapper** and **makefile**.
- Creates a `.tox` folder where environments are stored.

---

# pyproject.toml
- Used for configuring Python projects (alternative to setup.cfg).
- Contains metadata:
  - Build system info
  - Package name, version, author, license
  - Dependencies
- Works with modern packaging tools (e.g., Poetry, Flit, setuptools).

---

# setup.cfg
- Used by **setuptools** for project packaging and installation.
- Stores configuration options such as:
  - Metadata (name, version, author)
  - Dependency lists
  - Entry points
  - Other setup-related settings.

---

# Testing Python Applications

## Types of Testing
1. Automated Testing
2. Manual Testing

## Modes of Testing
1. Unit Testing (test individual functions/modules)
2. Integration Testing (test how components work together)

## Common Testing Frameworks
- pytest
- unittest
- robotframework
- selenium
- behave
- doctest

---

# Code Style, Formatting, and Linting

## Popular Tools
1. pylint – Checks Python code for errors and enforces coding standards.
2. flake8 – Combines multiple tools (pylint, pycodestyle, mccabe) in one.
3. pycodestyle – Checks Python code against PEP 8 style guidelines.

---

# Summary
- Use `requirements.txt` for production dependencies.
- Use `requirements_dev.txt` for development/testing dependencies.
- Use `tox.ini` for testing across different Python versions.
- Use `pyproject.toml` or `setup.cfg` for project configuration.
- Follow coding standards with tools like flake8 or pylint.
- Test your application with frameworks like pytest or unittest.
