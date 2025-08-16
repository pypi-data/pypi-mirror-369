# GitHub Setup Guide

This guide explains how to set up GitHub Actions for automated testing and PyPI publishing for the CSE.LK package.

## 🚀 GitHub Actions Workflows

The package includes three main GitHub Actions workflows:

### 1. **Tests Workflow** (`.github/workflows/test.yml`)
- **Triggers:** Push to `main`/`develop` branches, Pull Requests
- **Purpose:** Run tests on multiple Python versions and operating systems
- **Features:**
  - Tests on Python 3.7-3.12
  - Tests on Ubuntu, Windows, and macOS
  - Code coverage reporting
  - Linting with Black, Flake8, and MyPy

### 2. **PyPI Publishing** (`.github/workflows/publish-to-pypi.yml`)
- **Triggers:** GitHub Releases (published)
- **Purpose:** Automatically publish stable releases to PyPI
- **Features:**
  - Pre-publish testing
  - Package building and validation
  - Secure publishing with trusted publishing

### 3. **Test PyPI Publishing** (`.github/workflows/publish-to-test-pypi.yml`)
- **Triggers:** Beta/alpha/RC tags, Manual dispatch
- **Purpose:** Publish pre-release versions to Test PyPI
- **Features:**
  - Testing before publication
  - Pre-release version handling

## 🔧 Initial Setup

### Step 1: Repository Setup

1. **Create GitHub Repository:**
   ```bash
   # Navigate to your package directory
   cd /path/to/cse.lk
   
   # Initialize git (if not already done)
   git init
   git add .
   git commit -m "Initial commit: CSE.LK Python package"
   
   # Add remote (replace with your GitHub username/org)
   git remote add origin https://github.com/your-username/cse.lk.git
   git push -u origin main
   ```

2. **Create Required Branches:**
   ```bash
   # Create develop branch for development work
   git checkout -b develop
   git push -u origin develop
   ```

### Step 2: Configure GitHub Environments

1. **Go to Repository Settings > Environments**

2. **Create `pypi` Environment:**
   - Name: `pypi`
   - Protection rules (recommended):
     - Required reviewers: Add yourself or team members
     - Wait timer: 0 minutes
     - Deployment branches: `main` only

3. **Create `test-pypi` Environment:**
   - Name: `test-pypi`
   - Protection rules (optional):
     - Deployment branches: Any branch

### Step 3: Set Up PyPI Trusted Publishing

Instead of using API tokens, we'll use PyPI's trusted publishing feature for enhanced security.

#### For PyPI (Production):

1. **Go to [PyPI](https://pypi.org/) and log in**

2. **Navigate to Account Settings > Publishing**

3. **Add a new trusted publisher:**
   - **Repository owner:** `your-username`
   - **Repository name:** `cse.lk`
   - **Workflow name:** `publish-to-pypi.yml`
   - **Environment name:** `pypi`

#### For Test PyPI:

1. **Go to [Test PyPI](https://test.pypi.org/) and log in**

2. **Navigate to Account Settings > Publishing**

3. **Add a new trusted publisher:**
   - **Repository owner:** `your-username`
   - **Repository name:** `cse.lk`
   - **Workflow name:** `publish-to-test-pypi.yml`
   - **Environment name:** `test-pypi`

### Step 4: Configure Codecov (Optional)

For code coverage reporting:

1. **Go to [Codecov](https://codecov.io/) and sign up with GitHub**

2. **Add your repository to Codecov**

3. **Add Codecov badge to README.md:**
   ```markdown
   [![codecov](https://codecov.io/gh/your-username/cse.lk/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/cse.lk)
   ```

## 🏷️ Release Process

### Creating a Stable Release:

1. **Update version in `setup.py`:**
   ```python
   version="1.0.0",
   ```

2. **Update CHANGELOG.md with release notes**

3. **Create and push a tag:**
   ```bash
   git checkout main
   git pull origin main
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Create GitHub Release:**
   - Go to GitHub > Releases > Create a new release
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

5. **The PyPI workflow will automatically trigger and publish to PyPI**

### Creating a Pre-release:

1. **Update version with pre-release suffix:**
   ```python
   version="1.1.0-beta1",
   ```

2. **Create and push a tag:**
   ```bash
   git tag v1.1.0-beta1
   git push origin v1.1.0-beta1
   ```

3. **The Test PyPI workflow will automatically trigger**

## 🔍 Monitoring Workflows

### Viewing Workflow Runs:
- Go to your repository > Actions tab
- Click on any workflow run to see details
- Check logs for any failures

### Common Issues and Solutions:

1. **Tests failing:**
   - Check the test logs in the Actions tab
   - Run tests locally: `python -m pytest tests/ -v`
   - Fix any failing tests before creating releases

2. **Linting errors:**
   - Run locally: `python -m black cse_lk/ tests/ examples/`
   - Run: `python -m flake8 cse_lk/ tests/ examples/`

3. **PyPI publishing fails:**
   - Ensure trusted publishing is set up correctly
   - Check that the package name is available on PyPI
   - Verify the version number hasn't been used before

4. **Environment protection rules:**
   - If publishing is blocked, check environment protection rules
   - Required reviewers must approve the deployment

## 🛡️ Security Best Practices

1. **Use Trusted Publishing:** Never store API tokens in repository secrets
2. **Environment Protection:** Use environment protection rules for production deployments
3. **Branch Protection:** Enable branch protection on `main` branch
4. **Review Process:** Require pull request reviews for important changes

## 📈 Workflow Badges

Add these badges to your README.md:

```markdown
[![Tests](https://github.com/your-username/cse.lk/actions/workflows/test.yml/badge.svg)](https://github.com/your-username/cse.lk/actions/workflows/test.yml)
[![PyPI](https://github.com/your-username/cse.lk/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/your-username/cse.lk/actions/workflows/publish-to-pypi.yml)
[![PyPI version](https://badge.fury.io/py/cse.lk.svg)](https://badge.fury.io/py/cse.lk)
```

## 🔄 Manual Workflow Triggers

You can manually trigger workflows:

1. **Go to Actions tab in your repository**
2. **Select the workflow you want to run**
3. **Click "Run workflow" button**
4. **Choose branch and click "Run workflow"**

This is useful for:
- Testing the publishing workflow before a release
- Running tests on a specific branch
- Emergency publishes

## 📝 Customization

### Modifying Test Matrix:
Edit `.github/workflows/test.yml` to change:
- Python versions tested
- Operating systems
- Test commands

### Adding More Checks:
You can add additional workflow steps like:
- Security scanning
- Documentation building
- Performance benchmarks
- Integration tests

### Custom Release Process:
Modify workflows to fit your specific release process:
- Add changelog generation
- Send notifications
- Update documentation
- Deploy to other platforms

## 🆘 Troubleshooting

If you encounter issues:

1. **Check the Actions logs** for detailed error messages
2. **Test locally** to reproduce issues
3. **Review GitHub Actions documentation** for specific actions
4. **Check PyPI documentation** for publishing requirements
5. **Open an issue** in this repository for help

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/) 