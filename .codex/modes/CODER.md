
# Coder Mode

> **Note:** All contributor mode documentation and related process notes must be placed in the `.codex/instructions/` folder within the relevant service directory (e.g., `WebUI/.codex/instructions/`, `Rest-Servers/.codex/instructions/`). Follow the documentation structure and naming conventions in that folder. See examples in each service's `.codex/instructions/`.


## Purpose
For contributors actively writing, refactoring, or reviewing code. Coder Mode emphasizes high-quality, maintainable, and well-documented contributions that are easy for others to understand and build upon. All technical documentation and implementation notes should be placed in `.codex/implementation/` within the relevant service and kept in sync with code changes.


## Guidelines
- Follow all repository coding standards, style guides, and best practices.
- **MANDATORY**: Run linting before every commit. For backend Python code: `ruff check . --fix` and address any remaining issues manually. See `.codex/implementation/linting-standards.md` for details.
- Regularly review the root `.codex/tasks/` folder for new or assigned tasks, and pick up work from there as requested by the Task Master or project leads.
- Write clear, maintainable, well-commented, and well-documented code with meaningful variable and function names.
- Add or update tests for all changes; ensure high test coverage and passing tests.
- Use the recommended tools (`uv` for Python, `bun` for Node/React) for consistency and reproducibility.
- When working on frontend features, review the Svelte documentation and existing components in `frontend/src/`. The application uses a web-based architecture with a Svelte frontend and Quart backend.
- Keep documentation in sync with code changes; update or create docs in `.codex/implementation/` and `.codex/instructions/` in the relevant service as needed.
- Update documentation in `.codex/implementation/` and `.codex/instructions/` whenever a comment is added to a pull request, ensuring all new information, clarifications, or decisions are accurately reflected.
- Break down large changes into smaller, reviewable commits or pull requests.
- Review your own code before submitting for review, checking for errors, clarity, and completeness.
- **Never edit audit or planning files (see Prohibited Actions below).**

## Typical Actions
- Review the root `.codex/tasks/` folder for new or assigned tasks
- **Run linting checks** (`ruff check . --fix`) before starting work and before each commit
- Implement new features or enhancements
- Fix bugs or technical debt
- Refactor modules for clarity, performance, or maintainability
- Update or write documentation in `.codex/implementation/` or `.codex/instructions/` in the relevant service
- Review code from others and provide constructive feedback
- Write or update tests
- **Ensure all linting issues are resolved** before submitting pull requests

## Prohibited Actions
**Do NOT edit audit or planning files.**
- Never modify files in `.feedback/`, `.codex/audit/`, `.codex/planning`, or `.codex/review` (or any other audit/planning directories). 
    - These are managed by Task Masters, Auditors, and Reviewers only.
- These files are read-only for coders. Editing them disrupts project planning and audit processes, and is grounds for removal from the repository.
- If you believe a planning or audit file needs to be updated, notify the Task Master instead of editing it yourself.
    - Ways to notify Task Master
        - update the task file with comments (Recommended)
        - tell the reviewer that sent you the request
        - add it to your pr message (Not recommended)
        - add comments in the code (Best way)

## Communication
- Announce start, progress, and completion of tasks using the team communication command in `AGENTS.md`.
- Clearly describe the purpose and context of your changes in commit messages and pull requests.
- Reference related issues, documentation, or discussions when relevant.
- Place technical documentation, design notes, and implementation details in `.codex/implementation/` or `.codex/instructions/` in the relevant service to keep knowledge accessible for the team.
