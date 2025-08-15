
# shipctl

**shipctl** is a command-line tool to upload and download files or directories to an OCI-compatible registry as artifacts.

## Features

- Upload any files or directories to OCI registries
- Download artifacts from OCI registries
- Simple CLI interface: `shipctl up` and `shipctl down`
- Supports authentication and custom output directories
- CLI options can also be set via environment variables

## Installation

```bash
pip install shipctl
```

## Usage

### Upload an artifact

```bash
shipctl up --target <oci-target> --username <user> --password <pass> --files <file1> --files <file2>
```

### Download an artifact

```bash
shipctl down --target <oci-target> --username <user> --password <pass> --outdir ./output-directory
```

### Options

- `--target`   : Target OCI artifact (required)
- `--username` : Username for authentication (required)
- `--password` : Password for authentication (required)
- `--files`    : Files or directories to upload (for `up`)
- `--outdir`   : Output directory for downloads (for `down`, default: `./artifacts`)

#### Environment Variables

All CLI options can also be set using environment variables:

- `SHIPCTL_OCI_TARGET`   → `--target`
- `SHIPCTL_OCI_USERNAME` → `--username`
- `SHIPCTL_OCI_PASSWORD` → `--password`
- `SHIPCTL_OCI_FILES`    → `--files`
- `SHIPCTL_OCI_OUTDIR`   → `--outdir`

For example:

```bash
export SHIPCTL_OCI_TARGET=your-oci-target
export SHIPCTL_OCI_USERNAME=your-username
export SHIPCTL_OCI_PASSWORD=your-password
shipctl up --files file1 --files file2
```

## License

This project is licensed under the Apache 2.0 License. For more information, see the [license](./license).
