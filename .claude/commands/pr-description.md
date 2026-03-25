# Write/Update PR Description

Write or update the pull request description for the current branch and push it to GitHub. Follow the project's PR template guidelines.

## Steps

1. Check for an existing PR: `gh pr view --json title,body,url,number`
2. Read the PR template: `.github/PULL_REQUEST_TEMPLATE.md`
3. Get the branch diff: `git diff main...HEAD --stat`
4. Get commit history: `git log main..HEAD --oneline`

## Writing the Description

Follow the template structure:
- **Summary**: Prose explaining what the PR does (not just bullet points of changes)
- **Why is this change being made?**: Focus on the problem being solved and the approach taken
- **Steps to test the change?**: Include test commands and key files to review

## Updating the PR

Use the GitHub API via gh to update the PR body:

```bash
gh api repos/{owner}/{repo}/pulls/{number} -X PATCH -f body="..."
```

This is more reliable than `gh pr edit` for complex descriptions.

## Push Changes

After updating the description, push any uncommitted changes to the remote.
