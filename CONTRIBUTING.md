# Contributing Guidelines

## Branching Strategy

### Main Branches
- `main`: Production branch - contains stable, released code
- `development`: Integration branch - where features are combined and tested

### Feature Development Process

1. **Create an Issue**
   - All new features should start with an issue
   - Use the feature request template
   - Get issue number for branch naming

2. **Branch Naming Convention**
   - Format: `feature/[issue-number]-short-description`
   - Example: `feature/42-add-pdf-parsing`

3. **Development Workflow**
   - Create feature branch from `development`
   - Make your changes in small, focused commits
   - Keep branch up to date with `development`
   - Write tests if applicable

4. **Pull Request Process**
   - Create PR to merge into `development`
   - Fill out PR template completely
   - Request review from team members
   - Address review comments
   - Keep PR up to date with `development`

5. **Code Review Requirements**
   - At least one approval required
   - All discussions must be resolved
   - Branch must be up to date
   - All checks must pass

6. **Merging**
   - Only merge into `development` via PR
   - Use squash merge for clean history
   - Delete feature branch after merge

7. **Release Process**
   - Releases are made by merging `development` into `main`
   - Tag releases with semantic version
   - Update changelog

## Best Practices

1. **Commits**
   - Write clear commit messages
   - Keep commits focused and atomic
   - Reference issue number in commits

2. **Documentation**
   - Update README.md if needed
   - Add inline code comments
   - Update API documentation

3. **Testing**
   - Add tests for new features
   - Ensure all tests pass
   - Test edge cases

## Getting Help

- Check existing issues and documentation
- Ask questions in PR comments
- Reach out to maintainers