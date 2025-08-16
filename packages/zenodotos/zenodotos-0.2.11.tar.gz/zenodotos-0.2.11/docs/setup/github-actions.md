# GitHub Actions Workflows

This document describes the automated workflows using GitHub Actions for package releases and testing.

## Overview

The GitHub Actions workflows provide a separated approach to package releases and testing:

1. **Automated Package Release** - Publishes packages to PyPI/TestPyPI
2. **Test Package Installation** - Manually triggered testing with configurable parameters

This separation addresses the challenges of index propagation delays and provides more flexible testing options.

### Why Separation?

The release process was separated into two independent workflows to solve specific problems:

- **Index Propagation Delays**: PyPI/TestPyPI indexes take time to propagate changes, causing testing to fail immediately after publishing
- **Fixed Wait Times**: The previous combined workflow used fixed wait times that weren't suitable for all scenarios
- **Difficult Debugging**: When issues occurred, it was hard to isolate whether the problem was in publishing or testing
- **Blocking Releases**: Testing delays prevented releases from completing quickly

The new separated approach resolves these issues by providing independent execution, flexible timing, and clear separation of concerns.

## Workflow Files

### Automated Package Release
- **Location**: `.github/workflows/release.yml`
- **Trigger**: Release published
- **Environment**: Ubuntu latest with Python 3.11

### Test Package Installation
- **Location**: `.github/workflows/test-package.yml`
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

### Automated Release Process

1. **Create a release** on GitHub:
   - Go to Releases → Create a new release
   - Tag version: `v0.2.10` (with `v` prefix)
   - Title: `v0.2.10`
   - Add release notes
   - Publish release

2. **Workflow automatically runs**:
   - Publishes to TestPyPI and PyPI
   - Updates release with package information
   - Completes quickly without testing delays

### Manual Testing Process

1. **Trigger test workflow**:
   - Go to Actions → Test Package Installation
   - Click "Run workflow"
   - Configure parameters:
     - Package: `zenodotos`
     - Version: `0.2.10` (or leave empty for latest)
     - Target Index: `both` (or specific index)
     - Wait Time: `300` (5 minutes, adjust as needed)
     - Clean After: `true` (recommended)

2. **Workflow executes**:
   - Waits for package availability
   - Tests installation and functionality
   - Provides detailed results

### Version Format

The release workflow validates version format:
- Must be semantic versioning: `X.Y.Z`
- Examples: `0.2.2`, `1.0.0`, `2.1.3`
- Invalid: `0.2`, `v0.2.2`, `0.2.2-beta`

## Workflow Steps

### Automated Package Release Workflow

#### 1. Setup and Validation
- **Checkout**: Clone repository with full history
- **Python Setup**: Install Python 3.11
- **uv Setup**: Install latest uv package manager
- **Dependencies**: Install project dependencies
- **Tests**: Run full test suite (pytest, ruff, ty)
- **Version Validation**: Validate version format

#### 2. Publishing
- **TestPyPI Release**: Publish to TestPyPI using `./scripts/release.sh --testpypi`
- **PyPI Release**: Publish to production PyPI using `./scripts/release.sh --pypi`

#### 3. Release Management
- **Verify Git Tag**: Ensure Git tag exists
- **Update Release**: Add package information to GitHub release

### Test Package Installation Workflow

#### 1. Setup and Configuration
- **Checkout**: Clone repository
- **Python Setup**: Install Python 3.11
- **uv Setup**: Install latest uv package manager
- **Configuration Display**: Show test parameters

#### 2. Testing (TestPyPI)
- **Availability Check**: Wait for package availability with configurable timeout
- **Installation Test**: Test package installation and functionality

#### 3. Testing (PyPI)
- **Availability Check**: Wait for package availability with configurable timeout
- **Installation Test**: Test package installation and functionality

#### 4. Summary
- **Results Display**: Show test results and next steps

## Output

### Release Workflow Success
- ✅ Package published to TestPyPI
- ✅ Package published to PyPI
- ✅ Git tag verified: `v{version}`
- ✅ GitHub release updated
- 📦 PyPI link: `https://pypi.org/project/zenodotos/{version}/`
- 🏷️ Release link: `https://github.com/{repo}/releases/tag/v{version}`

### Test Workflow Success
- ✅ Package availability confirmed
- ✅ Package installation successful
- ✅ CLI functionality verified
- ✅ Library functionality verified
- 📋 Detailed test results and next steps

### Release Workflow Failure Points
- ❌ Version format validation
- ❌ Test suite failures
- ❌ TestPyPI publishing failure
- ❌ PyPI publishing failure
- ❌ Git operations failure

### Test Workflow Failure Points
- ❌ Package not available (index propagation delay)
- ❌ Package installation failure
- ❌ CLI functionality failure
- ❌ Library functionality failure

## Configuration

### Environment Variables

```yaml
env:
  PYTHON_VERSION: '3.11'
```

### Release Workflow
The release workflow is triggered automatically when a release is published and doesn't require manual inputs.

### Test Workflow Inputs

```yaml
inputs:
  package_name:
    description: 'Package name to test'
    required: true
    default: 'zenodotos'
    type: string
  version:
    description: 'Version to test (leave empty to use latest GitHub release)'
    required: false
    type: string
  target_index:
    description: 'Target index to test'
    required: true
    default: 'both'
    type: choice
    options:
      - testpypi
      - pypi
      - both
  wait_time:
    description: 'Wait time for index propagation (seconds)'
    required: false
    default: '300'
    type: string
```

### Configuration Examples

#### Test Specific Version from TestPyPI
```yaml
package_name: zenodotos
version: 0.2.10
target_index: testpypi
wait_time: 300
```

#### Test Latest Release from Both Indexes
```yaml
package_name: zenodotos
version: ""  # Empty to auto-detect latest GitHub release
target_index: both
wait_time: 600  # 10 minutes
```

#### Test Different Package
```yaml
package_name: requests
version: 2.31.0
target_index: pypi
wait_time: 60
```

## Benefits of Separation

### 1. **Reliability**
- Release workflow completes quickly and reliably
- No blocking on index propagation delays
- Clear separation of concerns

### 2. **Flexibility**
- Testing can be done anytime after release
- Configurable wait times and retry logic
- Can test multiple scenarios independently

### 3. **Debugging**
- Easy to isolate issues (publishing vs. testing)
- Can retry testing without re-publishing
- Detailed logs for each step

### 4. **Maintenance**
- Simpler workflows with single responsibilities
- Easier to modify and extend
- Better error handling and recovery

## Troubleshooting

### Release Workflow Issues

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

#### Release Workflow Succeeds but Package Not Available
**Solution**: This is expected due to index propagation delays. Use the test workflow to verify availability when ready.

### Test Workflow Issues

#### Package Not Available Error
```
❌ Package zenodotos==0.2.10 is NOT AVAILABLE on PyPI
```
**Solution**:
- Increase wait time for index propagation
- Check if package was actually published
- Verify package name and version are correct

#### Installation Failure
```
❌ Failed to install zenodotos after 5 attempts
```
**Solution**:
- Check package dependencies and compatibility
- Verify package structure and entry points
- Review package metadata and configuration

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

## Migration from Combined Workflow

The previous workflow combined publishing and testing, which caused issues due to:
- Index propagation delays blocking release completion
- Fixed wait times not suitable for all scenarios
- Difficult debugging when issues occurred

The new separated approach resolves these issues by:
- **Independent execution**: Publishing and testing are separate
- **Flexible timing**: Configurable wait times for testing
- **Better error handling**: Clear separation of concerns
- **Improved reliability**: No blocking on external factors

## Future Enhancements

### Potential Improvements:
1. **Workflow Linking**: Optional linking between release and test workflows
2. **Automated Testing**: Scheduled testing after release
3. **Notification Integration**: Slack/email notifications for test results
4. **Advanced Configuration**: More granular test parameters
5. **Cross-Platform Testing**: Test on different operating systems

### Integration Options:
- **Manual**: Run test workflow after release (current approach)
- **Semi-Automated**: Release workflow triggers test workflow with delay
- **Fully Automated**: Scheduled testing with automatic retries

### Technical Enhancements:
- **Automatic Versioning**: Extract version from conventional commits
- **Release Notes**: Auto-generate from commit messages
- **Package Signing**: Add GPG signing for enhanced security
- **Multi-platform**: Support multiple Python versions
- **Rollback**: Add ability to rollback releases
