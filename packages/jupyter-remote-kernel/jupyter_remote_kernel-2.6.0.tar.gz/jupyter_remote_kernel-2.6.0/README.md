# Jupyter Remote Kernel

A CLI tool for launching and managing remote Jupyter kernels over SSH port forwarding.

## Features

- **SSH tunneling** for all five Jupyter ZMQ channels (`shell`, `iopub`, `stdin`, `control`, `hb`)
- **Support Bastion** you can use -J user@basion:port to forward into your private network
- **Kernel spec management**: add, list, and delete remote kernels for seamless integration with Jupyter and VS Code
- **Graceful tunnel management**: start and stop SSH tunnels as needed

---

## Simple Architecture

```plaintext
[ JupyterLab / VS Code ]
            |
    ~/.local/share/jupyter/kernels/remote_cuda/kernel.json
            |
     [ remote_kernel CLI ]
            |
  SSH tunnel  <====>  [ Remote Host: ipykernel + Python ]
            |
    /tmp/<connection file> is copied to remote host before starting
```
---

## Installation

```bash
pip install jupyter_remote_kernel
```

---

## Usage

## Kernel Spec Management

### Add a remote kernel

Registers a new kernel spec so it appears in Jupyter and VS Code:

```bash
remote_kernel add --endpoint ubuntu@11.0.0.10:22 -J gw@1.1.1.1:3223 --name "Remote CUDA"
```

This creates a kernel spec at `~/.local/share/jupyter/kernels/remote_cuda/kernel.json`:

```json
{
  "argv": [
    "/path/to/remote_kernel",
    "--endpoint", "ubuntu@11.0.0.10:22",
    "-J", "gw@1.1.1.1:3223",
    "-f", "{connection_file}"
  ],
  "display_name": "Remote CUDA",
  "language": "python"
}
```

### List all registered kernels

```bash
remote_kernel list
```

Example output:
```
slug: remote_cuda
  name: Remote CUDA
  endpoint: ubuntu@11.0.0.10:22
---
slug: gpu_lab
  name: GPU Lab
  endpoint: dev@10.0.0.5:2222
---
```

### Delete a kernel

Delete by slug (preferred):

```bash
remote_kernel delete remote_cuda
```

Or by display name:

```bash
remote_kernel delete "Remote CUDA"
```

Both remove the kernel spec from `~/.local/share/jupyter/kernels/<slug>`.

---

## Notes

- Slug names are lowercased from the display name, with spaces and dashes converted to underscores.
- **SSH jump host (bastion) support:**
  If your remote server is only accessible via a jump host (bastion), simply configure with -J.

---

## Example Workflow

```bash
remote_kernel add --endpoint ubuntu@11.0.0.10:22 --name "Remote CUDA"
remote_kernel list
remote_kernel delete remote_cuda
remote_kernel --kill
```

---

## Integration with JupyterLab and VS Code

Once a remote kernel is registered, it will appear in the JupyterLab and VS Code kernel selector.  
Select it as you would any local kernel to launch a remote session.

---

## License

Apache License Version 2.0, January 2004# Changelog

## Changelog

### [2.3.3] - 2025-07-31

### New Features

1. **add `rkernel` Command**  


### [2.3.2] - 2025-07-31

### New Features

1. **`remote_kernel sync` Command**  
   Added a `sync` subcommand to copy files between local and remote hosts (native `scp` by default, falls back to Paramiko SFTP).  
   Supports jump hosts (`-J`) and can be used independently of kernel operations.

2. **Expanded Native SSH Support**  
   Unified native `ssh` and `scp` handling across all subcommands for performance and stability, including tunneling and file transfer.

### Bug Fixes

- Fixed issues with stale connection files by ensuring they are cleaned after sync and kernel shutdown.  
- Improved stability when using `--python` for remote interpreter configuration during kernel startup.


### [2.3.0] - 2025-07-31

### New Features

1. **Native SSH Support via Config**  
   Added configuration option to force system `ssh` usage for all commands and tunnels, ensuring optimal performance and reliability.

2. **Native SCP Support**  
   File transfers now use the system `scp` binary by default for faster and more stable copying, with automatic fallback to Paramiko SFTP if unavailable.

3. **Simplified Execution Flow**  
   Removed built-in retry logic; users now manually retry commands, providing clearer control and output.

### Bug Fixes

- Fixed inconsistencies in tunnel initialization when using native SSH.  
- Resolved race conditions between tunnel setup and command execution.  
- Improved cleanup handling for kernel exit, preventing leftover remote files and tunnels.  
- General stability improvements across SSH, SCP, and tunnel workflows.

### [2.2.0] - 2025-07-30

### New Features

1. **Native SSH by Default**  
   Uses the system `ssh` binary for faster, more stable, fully interactive sessions and tunnel handling.  

2. **Paramiko Fallback**  
   Automatically falls back to Paramiko when `ssh` is unavailable for compatibility.  

3. **Simplified Error Handling**  
   Removed automatic retries — users now manually retry failed commands or connections.

### [2.1.1] - 2025-07-28

### New Features

1. **Full Python SSH and SCP**  
   Replaced system `ssh`/`scp` with Paramiko and SFTP, including native `-J` jump host support.

2. **Integrated SSH Tunneling**  
   Managed Jupyter port forwarding via `SSHTunnelForwarder`, tied to command execution to prevent dangling tunnels. Retry interval reduced to 5s.

3. **Interactive Sessions**  
   Added `SSHWrapper.connect()` for a full interactive shell with `Ctrl+D` to exit.

4. **Kernel Auto-Cleanup**  
   Cleans up JSON connection files on kernel failure or exit to avoid stale entries.

5. **CLI Streamlining**  
   Removed `--kill`; tunnels and kernels now auto-clean. Commands supported: `add`, `list`, `delete`, `connect`, and kernel execution.

### Bug Fixes

- Resolved Paramiko `sock` conflicts between tunnels and commands.  
- Fixed race conditions between tunnel setup and execution.  
- Reduced log spam with 5s tunnel retry delay.  
- Ensured stale kernel sessions and files are properly cleaned up.  
- Improved stability when tunnels remained active after kernel shutdown.

### [2.0.0] - 2025-07-28

### Major Changes

- **Migrated to `paramiko` and `sshtunnel`**  
  All SSH and port forwarding handled via Python libraries, improving portability and error handling.  

- **Jump Host Support**  
  Added robust `-J` bastion handling using `sshtunnel`, removing dependency on system `ssh`.  

### New Features

- Automatic dependency installation for `paramiko` and `sshtunnel`.  
- Improved logging with version tracking.  
- Better process and tunnel management for `start_kernel`.  

### Breaking Changes

- System `ssh` and `scp` binaries no longer used by default.  
  Users may need to configure Paramiko keys separately.

### [1.6.0] - 2025-07-28

### Added

- `remote_kernel connect` — connect to a kernel by slug or list all kernels with jump host details.  
- `remote_kernel -v` — show version.  
- `remote_kernel -h` — show usage.