# Release Process

## Preparing for Release

1. **Update Version**: Update version numbers in relevant files if needed
2. **Test Locally**: Run the build script to ensure everything works
   ```bash
   python build.py
   ```
3. **Test the Binary**: Make sure the built executable works correctly

## GitHub Release Process

1. **Create a New Release** on GitHub:
   - Go to your repository → Releases → Create a new release
   - Choose a tag (e.g., `v1.0.0`)
   - Title: "PSN Tool v1.0.0"
   - Description: Copy from changelog or write release notes

2. **Trigger the Build**:
   - Publishing the release will automatically trigger the GitHub Actions workflow
   - The workflow will build binaries for Windows, Linux, and macOS
   - This takes about 10-15 minutes per platform

3. **Download Binaries**:
   - Once the workflow completes, the binaries will be attached to the release
   - Files will be named: `psntool-{platform}-v{version}{extension}`

## Binary Names

- **Windows**: `psntool-windows-v1.0.0.exe`
- **Linux**: `psntool-linux-v1.0.0` (no extension)
- **macOS**: `psntool-macos-v1.0.0` (no extension)

## Troubleshooting

### Build Fails
- Check the GitHub Actions logs for error messages
- Ensure all dependencies in `requirements.txt` are correct
- Test the build locally first with `python build.py`

### Binary Won't Run
- Check if it's a dependency issue (missing Qt libraries)
- Test on a clean system without Python installed
- Check file permissions (especially on Linux/macOS)

### Release Assets Missing
- Ensure the workflow completed successfully
- Check that the upload step didn't fail
- Re-run the workflow if needed

## Distribution

Once the release is created with binaries attached:

1. **GitHub Releases**: Users can download directly from GitHub
2. **Website**: Upload to your website if you have one
3. **Package Managers**: Submit to package managers if desired
4. **Social Media**: Announce the release

## Version Numbering

Use [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes
