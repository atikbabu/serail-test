# CLAUDE.md - AI Assistant Guidelines

This file provides guidance for AI assistants working with this codebase.

## Repository Overview

**Repository:** serail-test
**Owner:** atikbabu
**Status:** New repository (initial setup)

This repository is currently in the initial setup phase. The structure and conventions documented below should be followed as the project develops.

## Project Structure

```
serail-test/
├── CLAUDE.md          # AI assistant guidelines (this file)
└── .git/              # Git repository metadata
```

*Note: This structure will be updated as the project grows.*

## Development Guidelines

### Git Workflow

1. **Branch Naming Convention**
   - Feature branches: `feature/<description>`
   - Bug fixes: `fix/<description>`
   - AI-generated branches: `claude/<session-identifier>`

2. **Commit Messages**
   - Use clear, descriptive commit messages
   - Start with a verb in imperative mood (Add, Fix, Update, Remove, Refactor)
   - Keep the first line under 72 characters
   - Add body for complex changes

3. **Pull Requests**
   - Include a clear description of changes
   - Reference related issues if applicable
   - Ensure all tests pass before merging

### Code Conventions

*To be defined as the project develops. Common conventions include:*

- Consistent indentation (spaces vs tabs)
- Naming conventions for files, functions, and variables
- Documentation requirements
- Error handling patterns

### Testing

*Testing framework and conventions to be defined.*

## AI Assistant Instructions

### When Working on This Repository

1. **Always explore first** - Read existing code before making changes
2. **Follow existing patterns** - Match the style and conventions already in use
3. **Keep changes minimal** - Only modify what's necessary for the task
4. **Test your changes** - Run available tests and verify functionality
5. **Document significant changes** - Update relevant documentation

### Common Tasks

#### Setting Up the Project
```bash
# Clone the repository
git clone <repository-url>

# Install dependencies (when package.json exists)
npm install  # or yarn install
```

#### Running Tests
```bash
# To be defined when testing framework is set up
```

#### Building the Project
```bash
# To be defined when build system is configured
```

### Things to Avoid

- Do not commit sensitive information (API keys, credentials, etc.)
- Do not modify core configuration without understanding implications
- Do not introduce breaking changes without clear documentation
- Do not add unnecessary dependencies

## Maintenance

This CLAUDE.md file should be updated when:
- New major features or modules are added
- Development workflows change
- New conventions are established
- Build or test processes are updated

---

*Last updated: 2026-02-04*
