# Release Checklist

This checklist ensures a smooth and reliable release process for Zenodotos packages to PyPI.

## Pre-Release Preparation

### ✅ Code Quality Checks
- [ ] **All tests pass**: `uv run pytest`
- [ ] **Code coverage >80%**: Currently at 95.76%
- [ ] **Linting passes**: `uv run ruff check .`
- [ ] **Formatting is correct**: `uv run ruff format --check .`
- [ ] **Type checking passes**: `uv run ty check`
- [ ] **Security audit clean**: `uv run bandit -r src/`

### ✅ Documentation Updates
- [ ] **README.md** is up to date
- [ ] **API documentation** is current
- [ ] **User guides** reflect latest features
- [ ] **Changelog** is updated (if applicable)
- [ ] **Installation instructions** are correct

### ✅ Package Configuration
- [ ] **Version updated** in `pyproject.toml`
- [ ] **Dependencies** are correctly specified
- [ ] **Package metadata** is complete and accurate
- [ ] **Entry points** are correctly configured
- [ ] **License** information is correct

### ✅ Environment Setup
- [ ] **TestPyPI token** is set: `export TEST_PYPI_TOKEN="your-token"`
- [ ] **Production PyPI token** is set: `export PYPI_TOKEN="your-token"`
- [ ] **uv is installed** and working
- [ ] **Git repository** is clean and up to date

## Release Process

### ✅ Build and Test
- [ ] **Clean previous builds**: `rm -rf dist/ build/ *.egg-info/`
- [ ] **Build package**: `uv build`
- [ ] **Verify build artifacts**: Check `dist/` directory
- [ ] **Test package locally**: `uv pip install dist/zenodotos-*.tar.gz`

### ✅ Automated Publishing (GitHub Actions)
- [x] **Create GitHub release**: Triggers automatic publishing workflow
- [x] **Automatic TestPyPI publishing**: Handled by release workflow
- [x] **Automatic PyPI publishing**: Handled by release workflow
- [x] **Release completion**: Workflow completes quickly after publishing

### ✅ Manual Testing (Optional)
- [ ] **Run test workflow**: Go to Actions → Test Package Installation
- [ ] **Configure test parameters**: Package, version, target index, wait time
- [ ] **Verify TestPyPI installation**: Tests availability and installation
- [ ] **Verify PyPI installation**: Tests availability and installation
- [ ] **Review test results**: Check workflow output for success/failure

## Post-Release Verification

### ✅ Package Availability Verification
- [ ] **Use test workflow**: Go to Actions → Test Package Installation
- [ ] **Test both indexes**: Configure target_index to "both"
- [ ] **Set appropriate wait time**: 300s for TestPyPI, 600s for PyPI
- [ ] **Review availability results**: Check workflow output
- [ ] **Verify installation**: Confirm package installs and works correctly
- [ ] **Monitor propagation**: Re-run test workflow if needed

### ✅ Installation Testing
- [ ] **Clean environment test**: Install in fresh virtual environment
- [ ] **Different Python versions**: Test with Python 3.11, 3.12, 3.13
- [ ] **CLI commands work**: `zenodotos --help`, `zenodotos list-files --help`, etc.
- [ ] **Library imports work**: `import zenodotos`, `from zenodotos import Zenodotos`
- [ ] **Basic functionality**: Test core features work as expected

### ✅ Documentation Verification
- [ ] **PyPI page** displays correctly
- [ ] **Package description** is accurate
- [ ] **Installation instructions** work
- [ ] **Documentation links** are correct

### ✅ Git Repository Updates
- [ ] **Version changes committed**: `git add pyproject.toml`
- [ ] **Conventional commit message**: `git commit -m "feat: bump version to X.Y.Z"`
- [ ] **Changes pushed to main**: `git push origin main`
- [ ] **GitHub release created**: Go to Releases → Create new release
- [ ] **Tag version**: Use `vX.Y.Z` format (e.g., `v0.2.10`)
- [ ] **Publish release**: Triggers automated publishing workflow

**Versioning Notes**:
- Package version in `pyproject.toml`: `X.Y.Z` (without `v` prefix)
- Git tag: `vX.Y.Z` (with `v` prefix for semantic versioning)

## Automated Release (Current)

### ✅ GitHub Actions Setup
- [x] **Release workflow** created: `.github/workflows/release.yml`
- [x] **Test workflow** created: `.github/workflows/test-package.yml`
- [x] **Secrets configured**: `TEST_PYPI_TOKEN`, `PYPI_TOKEN`
- [x] **Release triggers** configured: `on: release: types: [published]`
- [x] **Quality gates** implemented: Tests must pass before publishing
- [x] **Separated workflows** for publishing and testing

### ✅ Automated Testing
- [x] **Pre-publishing tests** run automatically in release workflow
- [x] **Manual testing workflow** available for post-publishing verification
- [x] **Configurable wait times** for index propagation delays
- [x] **GitHub release version auto-detection** for testing
- [x] **Flexible testing options** (TestPyPI, PyPI, or both)

## Troubleshooting

### Common Issues and Solutions

#### Authentication Errors
- **Issue**: `403 Forbidden` or authentication failures
- **Solution**: Verify API tokens are correct and have proper permissions
- **Check**: `echo $TEST_PYPI_TOKEN` and `echo $PYPI_TOKEN`

#### Package Already Exists
- **Issue**: `File already exists` error
- **Solution**: Increment version number in `pyproject.toml`
- **Check**: PyPI doesn't allow overwriting existing versions

#### Build Failures
- **Issue**: `uv build` fails
- **Solution**: Check `pyproject.toml` syntax and dependencies
- **Check**: Run `uv build --dry-run` for detailed errors

#### Installation Failures
- **Issue**: Package installs but doesn't work
- **Solution**: Check entry points and package structure
- **Check**: Use the test workflow to verify installation

## Release Notes Template

When creating release notes, include:

```markdown
## Version X.Y.Z

### 🚀 New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes
- Fix 1 description
- Fix 2 description

### 🔧 Improvements
- Improvement 1 description
- Improvement 2 description

### 📚 Documentation
- Documentation update 1
- Documentation update 2

### 🔒 Security
- Security fix 1 (if applicable)

### 📦 Installation
```bash
pip install zenodotos==X.Y.Z
```

### 🔗 Links
- [PyPI Package](https://pypi.org/project/zenodotos/)
- [Documentation](https://zenodotos.readthedocs.io/)
- [GitHub Repository](https://github.com/ifosch/zenodotos/)
```

## Emergency Procedures

### Package Yanking
If a critical issue is discovered after release:

1. **Yank the package**: `uv publish --repository pypi --token "$PYPI_TOKEN" --yank`
2. **Create hotfix**: Fix the issue and create new version
3. **Release hotfix**: Follow normal release process
4. **Communicate**: Update documentation and notify users

### Rollback Process
If automated release fails:

1. **Check logs**: Review GitHub Actions logs
2. **Identify issue**: Determine root cause
3. **Fix locally**: Test fix manually
4. **Re-run workflow**: Create new GitHub release
5. **Verify**: Confirm successful release
6. **Test installation**: Use test workflow to verify package works

## Success Metrics

A successful release should achieve:

- ✅ **All tests pass** (242 tests, 95.76% coverage)
- ✅ **Package installs correctly** from both TestPyPI and PyPI
- ✅ **CLI functionality** works as expected
- ✅ **Library functionality** works as expected
- ✅ **Documentation** is accurate and helpful
- ✅ **No security issues** detected
- ✅ **User feedback** is positive (if applicable)

## Next Steps After Release

1. **Monitor downloads**: Check PyPI download statistics
2. **Monitor issues**: Watch for user-reported problems
3. **Update roadmap**: Mark completed features
4. **Plan next release**: Identify features for next version
5. **Gather feedback**: Collect user experience data
