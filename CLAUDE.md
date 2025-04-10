# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- Run app: `./run.sh` (web interface) or `./run.sh local` (script mode)
- Install dependencies: `pip install -r requirements.txt`
- Run direct script: `python generate_report.py --file data.xlsx --business busivet --title "Report Title" --location "Location" --date "Date"`

## Code Guidelines
- Use docstrings for all modules, classes, and functions
- Follow PEP 8 style guide for Python code
- Import order: standard library, third-party packages, local modules
- Use type hints for function parameters and return values
- Exception handling: log exceptions with appropriate level (error, warning, info)
- Naming: snake_case for variables/functions, CamelCase for classes
- Logging: use the established logging pattern (FileHandler + StreamHandler)
- File paths: use os.path.join for cross-platform compatibility
- Comments: clear and meaningful, explain "why" not "what"
- Keep functions focused on a single responsibility