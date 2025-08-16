# Example Package

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

# ppptoolbox

## Development and Deployment Workflow

### 1. Feature Development

- Create a new feature branch from `master`:
  ```sh
  git checkout master
  git pull origin master
  git checkout -b feature/my-feature
  ```
- Make your changes and commit them.
- Push your feature branch:
  ```sh
  git push origin feature/my-feature
  ```

### 2. Testing on Development

- Open a Pull Request (PR) from your feature branch to `development`.
- Once merged, the workflow will automatically build, test, and publish the package to **TestPyPI**.
- You can also manually trigger the workflow on `development` using the "Run workflow" button in GitHub Actions.

### 3. Releasing to Production (PyPI)

- After successful testing, open a PR from `development` to `master`.
- Merge the PR into `master`.
- Bump the version in `pyproject.toml` (if not already done).
- Create a new annotated tag on `master` for the release:
  ```sh
  git checkout master
  git pull origin master
  git tag -a vX.Y.Z -m "Release vX.Y.Z"
  git push origin vX.Y.Z
  ```
- The workflow will automatically build and publish the package to **PyPI** when a tag is pushed to `master`.

### 4. Notes

- **TestPyPI** is used for testing releases from the `development` branch or manual workflow runs.
- **PyPI** is used for production releases, triggered only by tags on the `master` branch.
- Each release version can only be published once to PyPI/TestPyPI. Bump the version for each new release.