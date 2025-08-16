# Backend Architecture

`filoma` provides three high-performance backends that automatically select the best option for your system.

## Backend Overview

### 🐍 Python Backend (Universal)
- **Always available** - works on any Python installation
- **Full compatibility** - complete feature set
- **Reliable fallback** - when other backends aren't available

### 🦀 Rust Backend (Fastest)
- **Best performance** - 2.5x faster than alternatives
- **Parallel processing** - automatic multi-threading
- **Auto-selected** - chosen by default when available
- **Same API** - drop-in replacement with identical output

### 🔍 fd Backend (Competitive)
- **Fast file discovery** - leverages the `fd` command-line tool
- **Advanced patterns** - supports regex and glob patterns
- **Hybrid approach** - fd for discovery + Python for analysis
- **Network optimized** - often best for NFS filesystems

## Automatic Selection

```python
from filoma.directories import DirectoryProfiler

# Automatically uses fastest available backend
profiler = DirectoryProfiler()
result = profiler.analyze("/path/to/directory")

# Check which backend was used
profiler.print_summary(result)
# Shows: "Directory Analysis: /path (🦀 Rust)" or "🔍 fd" or "🐍 Python"
```

## Manual Backend Selection

```python
# Force specific backend
profiler_rust = DirectoryProfiler(search_backend="rust")
profiler_fd = DirectoryProfiler(search_backend="fd")
profiler_python = DirectoryProfiler(search_backend="python")

# Check availability
print(f"Rust available: {profiler_rust.is_rust_available()}")
print(f"fd available: {profiler_fd.is_fd_available()}")
print(f"Python available: True")  # Always available
```

## Backend Comparison

```python
import time

backends = ["rust", "fd", "python"]
for backend in backends:
    profiler = DirectoryProfiler(search_backend=backend, show_progress=False)
    # Check if the specific backend is available
    if ((backend == "rust" and profiler.is_rust_available()) or
        (backend == "fd" and profiler.is_fd_available()) or
        (backend == "python")):  # Python always available
        start = time.time()
        result = profiler.analyze("/test/directory")
        elapsed = time.time() - start
        files_per_sec = result['summary']['total_files'] / elapsed
        print(f"{backend}: {elapsed:.3f}s ({files_per_sec:,.0f} files/sec)")
```

## When to Use Each Backend

| Use Case | Recommended Backend | Why |
|----------|-------------------|-----|
| **Large directories** | Auto (Rust preferred) | Best overall performance |
| **Network filesystems** | `fd` | Optimized for network I/O |
| **CI/CD environments** | Auto | Reliable with graceful fallbacks |
| **Maximum compatibility** | `python` | Always works, no dependencies |
| **DataFrame analysis** | Auto (Rust preferred) | Fastest DataFrame building |
| **Pattern matching** | `fd` | Advanced regex/glob support |

## Technical Details

All backends provide:
- **Identical APIs** - same function signatures and parameters
- **Same output format** - consistent data structures
- **Progress bars** - real-time feedback for large operations
- **Error handling** - graceful fallbacks and error reporting

### Performance Characteristics

- **Rust**: Best for CPU-intensive operations, parallel processing
- **fd**: Best for I/O-intensive operations, pattern matching
- **Python**: Most compatible, good baseline performance

### Backend Detection

```python
from filoma.directories import DirectoryProfiler
from filoma.core import FdIntegration

# Check what's available
profiler = DirectoryProfiler()
fd = FdIntegration()

print("Available backends:")
print(f"  🐍 Python: Always available")
print(f"  🦀 Rust: {'✅' if profiler.use_rust else '❌'}")
print(f"  🔍 fd: {'✅' if fd.is_available() else '❌'}")

if fd.is_available():
    print(f"  fd version: {fd.get_version()}")
```
