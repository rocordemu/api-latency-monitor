# Contributing to API Latency Monitor

Thank you for considering contributing to the API Latency Monitor project! We welcome contributions from the community to improve the application, add features, fix bugs, or enhance documentation. This guide outlines how to contribute effectively.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct.html). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainer at [your-email@example.com].

## How to Contribute

### Reporting Issues

If you find a bug, have a feature request, or encounter any problem:
1. Check the [issues tracker](https://github.com/rocordemu/api-latency-monitor/issues) to see if it has already been reported.
2. If not, open a new issue with:
   - A descriptive title.
   - Detailed description (steps to reproduce, expected vs. actual behavior).
   - Screenshots or logs if applicable.
   - Environment details (OS, Python version, Kubernetes version).
3. Use labels (e.g., "bug", "enhancement", "documentation") for categorization.

### Submitting Pull Requests

Pull requests (PRs) are the best way to propose changes. Follow these steps:
1. Fork the repository and create a branch from `main` (e.g., `feature/new-alert-rule`).
2. Make your changes, ensuring they align with the project's style and features.
3. Add or update tests in `src/tests/` if applicable.
4. Run tests locally: `pytest src/tests/test_poller.py`.
5. Commit with clear messages (e.g., "Add high error rate alert rule").
6. Push to your fork and open a PR against `main`.
7. In the PR description:
   - Explain the change and why it's needed.
   - Reference related issues (e.g., "Fixes #42").
   - Mention any breaking changes.
8. The CI workflow will run automatically; ensure it passes.
9. Respond to feedback during review.

PRs should be focused (one feature/fix per PR) and include documentation updates if relevant.

### Code Style and Standards

- **Python Code**: Follow PEP 8. Use Black for formatting and Flake8 for linting (configured in CI).
- **Commit Messages**: Use conventional commits (e.g., "feat: add Slack alert", "fix: handle invalid token").
- **Documentation**: Update `README.md` for new features or changes.
- **Testing**: Maintain 100% coverage for `poller.py` and `storage.py`.
- **Kubernetes Manifests**: Use consistent naming (e.g., `api-latency-monitor-` prefix) and include comments for clarity.
- **Security**: Do not commit secrets; use placeholders in examples.

### Development Setup

1. Clone your fork: `git clone https://github.com/your-username/api-latency-monitor.git`
2. Set up virtual environment and dependencies as per README.
3. Make changes, test locally.
4. Commit and push.

### Review Process

- PRs are reviewed by the maintainer within 3-5 days.
- Changes may be requested for style, tests, or clarity.
- Once approved, the PR will be merged.

### Other Ways to Contribute

- Improve documentation or add examples.
- Suggest new features in issues.
- Help with code reviews or testing PRs.

Thank you for contributing to make this project better!