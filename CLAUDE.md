# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This package automatically configures Python to use system certificates instead of bundled ones via truststore integration. It works by injecting a `.pth` file that bootstraps truststore when Python starts.

## Architecture

The package uses a simplified bootstrap process:
1. `pip_system_certs.pth` - Executed when Python starts, imports bootstrap module
2. `bootstrap.py` - Hooks into site module's customization points 
3. `wrapt_requests.py` - Calls truststore.inject_into_ssl() to globally configure system certificates

This replaces the complex monkey-patching approach with truststore's native SSL context injection.

## Development Commands

### Build and install locally:
```bash
pip install .
```

### Build wheel:
```bash
python setup.py bdist_wheel
```

### Run full test suite:
```bash
./run_test.sh  # Runs Docker-based integration tests
```

### Manual testing:
```bash
cd test
bash test.sh  # Run integration tests in current environment
```

## Testing Architecture

Tests use a self-signed certificate authority to verify the system certificate integration:
- `test/pki/` contains CA and server certificates
- `simple-https-server.py` runs HTTPS server with self-signed cert
- Tests verify requests fail before installing system cert, pass after

## Build System

Uses setuptools with custom commands:
- `BuildIncludePth` - Ensures .pth file is included in wheels
- `InstallCheck`/`DevelopCheck` - Verify .pth file installation
- Git versioning via `git-versioner` package

## Key Files

- `pip_system_certs.pth` - Bootstrap entry point
- `bootstrap.py` - Site module hooks
- `wrapt_requests.py` - Truststore injection logic