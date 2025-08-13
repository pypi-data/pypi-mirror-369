# env-check-utils

`env-check-utils` is a Python package that helps you inspect and manage your environment variables and `.env` files with ease.
It provides commands to validate `.env` files against a schema, auto-generate schemas, find unused variables, and scan code directories for environment variable usage.

---

## Installation

# Install the package from PyPI
pip install env-check-utils

---

## Usage

# Once installed, you can run it from the command line using:
env-check [OPTIONS]

Features
# Here are all the available options and their descriptions:

# 1️. Validate .env file against a schema
env-check --schema path/to/schema.json
# Validates your .env file against a provided JSON schema.
# Ensures that required environment variables exist and have the correct type/format.

# 2️. Auto-generate a schema.json from your .env file
env-check --generate-schema
# Scans your .env file and generates a schema.json automatically based on the variables found.
# Useful when starting a new project or documenting existing variables.

# 3️. Find unused environment variables
env-check --check-unused
# Checks for environment variables present in your .env file but not used anywhere in your project.
# Helps keep your environment files clean and free from unnecessary variables.

# 4️. Scan a specific code directory for environment variable usage
env-check --path path/to/code
# Scans the given directory for usage of environment variables.
# Useful for identifying where variables are referenced in your codebase.

---

Examples

# Example 1: Validate .env with a schema
env-check --schema config/schema.json

# Example 2: Auto-generate schema from .env
env-check --generate-schema

# Example 3: Find unused variables
env-check --check-unused

# Example 4: Scan a project folder
env-check --path ./src
