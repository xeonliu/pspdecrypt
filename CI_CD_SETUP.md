# CI/CD Setup for pspdecrypt Python Package

This repository is configured with GitHub Actions workflows for automated testing and publishing of the Python package.

## Workflows

### Python CI (`python-ci.yml`)

This workflow runs on every push and pull request to the `master` branch.

**Testing:**
- Tests across multiple platforms: Ubuntu and macOS
- Tests Python versions: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
- Installs system dependencies (OpenSSL, zlib)
- Builds the package
- Runs test suite
- Note: Windows testing is done via cibuildwheel (see below)

**Building:**
- Builds binary wheels for all platforms (Linux, Windows, macOS) using `cibuildwheel`
- Builds source distribution (sdist)
- Uploads artifacts for distribution

**Publishing:**
- Automatically publishes to PyPI when a release is created
- Publishes to Test PyPI on pushes to master branch (for testing)

## Platform-Specific Notes

### Windows Build Support
The package has been configured for cross-platform compatibility:
- **Compiler Flags**: Automatically detects MSVC on Windows and uses appropriate flags (`/O2 /std:c++14`) vs GCC/Clang flags on Unix (`-O3 -std=c++11 -Wno-deprecated-declarations`)
- **Library Linking**: Uses `libcrypto` and `zlib` on Windows, `crypto` and `z` on Unix-like systems
- **CI Testing**: Windows builds are tested via `cibuildwheel` which handles the complex Windows build environment

### macOS Build Support
- Uses Homebrew to install OpenSSL and zlib dependencies
- Supports both x86_64 and arm64 (Apple Silicon) architectures via cibuildwheel

### Linux Build Support
- Supports multiple distributions via cibuildwheel
- Uses standard package managers (apt, yum) for dependencies

## PyPI Publishing

### Setup Required

To enable publishing to PyPI, you need to:

1. **Enable Trusted Publishing on PyPI:**
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new "pending publisher" with these details:
     - PyPI Project Name: `pspdecrypt`
     - Owner: `xeonliu`
     - Repository name: `pspdecrypt`
     - Workflow name: `python-ci.yml`
     - Environment name: `pypi`

2. **Enable Trusted Publishing on Test PyPI (optional):**
   - Go to https://test.pypi.org/manage/account/publishing/
   - Add the same configuration with environment name: `test-pypi`

3. **Create GitHub Environments:**
   - Go to repository Settings → Environments
   - Create environment named `pypi`
   - Create environment named `test-pypi` (optional)

### How to Publish

1. **Test PyPI (automatic):**
   - Any push to `master` branch will automatically publish to Test PyPI
   - Useful for testing before official release

2. **PyPI (on release):**
   - Create a new release on GitHub with a version tag (e.g., `v1.0.1`)
   - The workflow will automatically build and publish to PyPI
   - The package will be available at https://pypi.org/project/pspdecrypt/

## Local Testing

To test the build process locally:

```bash
# Install build dependencies
pip install build wheel pybind11>=2.6.0

# Build source distribution
python -m build --sdist

# Build wheel
python -m build --wheel

# Install locally
pip install dist/pspdecrypt-*.whl

# Run tests
python test_python.py
```

## Wheel Building

The workflow uses `cibuildwheel` to build wheels for:
- Linux: x86_64 (manylinux)
- Windows: AMD64
- macOS: x86_64 and arm64 (Apple Silicon)

All Python versions from 3.7 to 3.12 are supported.

## Troubleshooting

**Build failures on Windows:**
- Ensure OpenSSL and zlib are available
- Check MSYS2 setup logs

**Build failures on macOS:**
- Verify Homebrew installation of openssl and zlib
- Check library paths are correctly set

**PyPI publishing failures:**
- Verify Trusted Publishing is configured correctly
- Check that GitHub environments are set up
- Ensure release tag matches version in setup.py

## Version Management

To release a new version:

1. Update version in both:
   - `setup.py` (line 56)
   - `pyproject.toml` (line 7)

2. Update `CHANGELOG_PYTHON.md` with changes

3. Create and push a git tag:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. Create a GitHub release from the tag
   - The workflow will automatically publish to PyPI

## Security

The workflow uses OpenID Connect (OIDC) Trusted Publishing, which:
- Doesn't require storing PyPI tokens in GitHub
- Provides automatic credential management
- Offers better security than traditional API tokens

No secrets need to be configured in GitHub for publishing to work.
