# Publish to your own GitHub repository

This archive is prepared for publishing; it has not been pushed to any account. Do not use another candidate's repository.

1. Create an empty repository named `GuidePath` in your GitHub account.
2. Extract the archive. Open a terminal inside its `guidepath` folder.
3. Review `.gitignore` and run `git status` before committing. Raw data, `.env`, model binaries and runs are excluded. Curated screenshots, reports, example JSON and code are included.
4. Run these commands, replacing `YOUR_USERNAME` with your actual account:

```bash
git init
git add .
git status
git commit -m "Add GuidePath detection and structured reasoning prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/GuidePath.git
git push -u origin main
```

If the folder is already a repository, inspect `git remote -v` and its working changes before using the existing remote; do not overwrite it blindly. Authenticate using GitHub's normal sign-in, never by putting a token in source files.

5. Upload the final trained `best.pt` as a GitHub Release asset or other direct downloadable artifact. Put its real URL and SHA-256 in `weights/README.md`. Do not commit a large checkpoint into ordinary Git history.
6. Copy measured outputs to `outputs/real` and reviewed failure screenshots to `docs/evidence/real_failures`. Update the status table only after reviewing them. Commit those evidence files, not the entire training cache.
7. Include the repository URL, direct weights URL and two-page memo in the application submission. A public repository does not automatically deploy the API; deployment remains a separate step.

The CI workflow runs software tests only. A green check is not proof of model quality or task completion.
