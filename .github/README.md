# GitHub Workflows

This directory contains GitHub Actions workflows for the AI Agent Education Platform.

## 🤖 CodeRabbit Review

The `coderabbit.yml` workflow automatically runs CodeRabbit AI code review on all pull requests.

### Features
- **Automatic Review**: Triggers on PR open, sync, and reopen events
- **Comprehensive Analysis**: Reviews code quality, security, performance, and best practices
- **Project-Specific**: Configured for our Python/FastAPI backend and React/TypeScript frontend
- **AI-Powered**: Uses CodeRabbit's AI to provide detailed feedback and suggestions

### Configuration
- Workflow file: `.github/workflows/coderabbit.yml`
- CodeRabbit settings: `.coderabbit.yaml` (in project root)
- Documentation: See `CONTRIBUTING.md` for detailed information

### Requirements
- No additional setup required
- Uses GitHub's built-in `GITHUB_TOKEN`
- Works with public and private repositories

### What It Reviews
- Security vulnerabilities
- Performance issues
- Code quality and maintainability
- Best practices adherence
- Documentation completeness
- Project-specific patterns (AI agents, database migrations, API design)

For more information about CodeRabbit and how to interpret its feedback, see the [Automated Code Review section in CONTRIBUTING.md](../CONTRIBUTING.md#automated-code-review).
