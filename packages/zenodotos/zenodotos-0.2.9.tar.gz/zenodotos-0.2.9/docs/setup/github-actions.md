# GitHub Actions Release Workflow

This document describes the automated release workflow using GitHub Actions.

## Overview

The GitHub Actions workflow automates the complete release process, orchestrating all three decoupled scripts:
1. **Publish** - Build and publish packages
2. **Verify** - Check package availability
3. **Test** - Test package installation

## Workflow File

- **Location**: `.github/workflows/release.yml`
- **Trigger**: Manual (workflow_dispatch)
- **Environment**: Ubuntu latest with Python 3.11

## Prerequisites

### GitHub Secrets

Configure these secrets in your GitHub repository:

1. **TEST_PYPI_TOKEN**
   - Your TestPyPI API token
   - Used for publishing to TestPyPI

2. **PYPI_TOKEN**
   - Your production PyPI API token
   - Used for publishing to PyPI

### Setup Instructions

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each token with the exact names above

## Usage

### Manual Trigger

1. Go to your GitHub repository
2. Navigate to **Actions** tab
3. Select **Manual Package Release** workflow
4. Click **Run workflow**
5. Fill in the parameters:
   - **Version**: New version number (e.g., `0.2.2`)
   - **Skip TestPyPI**: Check to skip TestPyPI and go directly to PyPI

### Version Format

The workflow validates version format:
- Must be semantic versioning: `X.Y.Z`
- Examples: `0.2.2`, `1.0.0`, `2.1.3`
- Invalid: `0.2`, `v0.2.2`, `0.2.2-beta`

## Workflow Steps

### 1. Setup and Validation
- **Checkout**: Clone repository with full history
- **Python Setup**: Install Python 3.11
- **uv Setup**: Install latest uv package manager
- **Dependencies**: Install project dependencies
- **Tests**: Run full test suite (pytest, ruff, ty)
- **Version Validation**: Validate version format

### 2. Version Update
- **Update pyproject.toml**: Set new version
- **Update uv.lock**: Regenerate lock file
- **Commit Changes**: Commit version bump to main branch

### 3. TestPyPI Release (Optional)
- **Publish**: Run `./scripts/release.sh --testpypi`
- **Wait**: Wait for propagation (30 seconds)
- **Verify**: Check availability with `./scripts/check-package-availability.sh`
- **Test**: Test installation with `./scripts/test-package-install.sh`

### 4. PyPI Release
- **Publish**: Run `./scripts/release.sh --pypi`
- **Wait**: Wait for propagation (60 seconds)
- **Verify**: Check availability with `./scripts/check-package-availability.sh`
- **Test**: Test installation with `./scripts/test-package-install.sh`

### 5. Git Operations
- **Create Tag**: Create Git tag `v{version}`
- **Push Tag**: Push tag to repository
- **Create Release**: Create GitHub release with notes

## Output

### Success
- ✅ Package published to TestPyPI (if enabled)
- ✅ Package published to PyPI
- ✅ Git tag created: `v{version}`
- ✅ GitHub release created
- 📦 PyPI link: `https://pypi.org/project/zenodotos/{version}/`
- 🏷️ Release link: `https://github.com/{repo}/releases/tag/v{version}`

### Failure Points
- ❌ Version format validation
- ❌ Test suite failures
- ❌ TestPyPI publishing failure
- ❌ TestPyPI availability check failure
- ❌ TestPyPI installation test failure
- ❌ PyPI publishing failure
- ❌ PyPI availability check failure
- ❌ PyPI installation test failure
- ❌ Git operations failure

## Configuration

### Environment Variables

```yaml
env:
  PYTHON_VERSION: '3.11'
```

### Workflow Inputs

```yaml
inputs:
  version:
    description: 'New version to release (e.g., 0.2.2)'
    required: true
    type: string
  skip_testpypi:
    description: 'Skip TestPyPI and go directly to PyPI'
    required: false
    type: boolean
    default: false
```

## Troubleshooting

### Common Issues

#### Version Format Error
```
❌ Error: Version must be in format X.Y.Z (e.g., 0.2.2)
```
**Solution**: Use semantic versioning format (e.g., `0.2.2`)

#### Token Authentication Error
```
❌ TEST_PYPI_TOKEN environment variable is not set
```
**Solution**: Configure GitHub secrets properly

#### Test Failures
```
❌ pytest failed
❌ ruff check failed
❌ ty failed
```
**Solution**: Fix code issues before releasing

#### Availability Check Timeout
```
❌ Package did not become available within the timeout period
```
**Solution**: Wait longer or check PyPI/TestPyPI status

### Debugging

1. **Check Workflow Logs**: View detailed logs in GitHub Actions
2. **Manual Testing**: Test scripts locally first
3. **Token Validation**: Verify tokens work manually
4. **Network Issues**: Check PyPI/TestPyPI status

## Best Practices

### Before Running
1. **Test Locally**: Run all scripts manually first
2. **Update Documentation**: Ensure docs are current
3. **Check Dependencies**: Verify all dependencies are up to date
4. **Review Changes**: Ensure all changes are committed

### During Release
1. **Monitor Progress**: Watch workflow execution
2. **Check Logs**: Review detailed logs for issues
3. **Verify Results**: Check PyPI and GitHub after completion

### After Release
1. **Test Installation**: Install from PyPI manually
2. **Update Documentation**: Update any version-specific docs
3. **Announce Release**: Notify users of new version

## Security Considerations

- **Token Security**: Never commit tokens to repository
- **Access Control**: Limit who can trigger workflows
- **Audit Logs**: Review workflow execution logs
- **Dependency Scanning**: Regularly update dependencies

## Future Enhancements

- **Automatic Versioning**: Extract version from conventional commits
- **Release Notes**: Auto-generate from commit messages
- **Package Signing**: Add GPG signing for enhanced security
- **Multi-platform**: Support multiple Python versions
- **Rollback**: Add ability to rollback releases
