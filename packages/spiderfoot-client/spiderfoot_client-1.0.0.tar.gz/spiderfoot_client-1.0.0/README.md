# SpiderFoot Client

A Python client library and command-line interface for the SpiderFoot OSINT automation tool API.

## Installation

```bash
pip install spiderfoot-client
```

## Library Usage

```python
from spiderfoot_client import SpiderFootClient

# Initialize client
client = SpiderFootClient(
    base_url="http://localhost:5001",
    username="admin", 
    password="your_password"
)

# Start a scan
result = client.start_scan(
    target="example.com",
    scan_name="My Scan",
    use_case="passive"
)
scan_id = result['id']

# Monitor scan progress
status = client.get_scan_status(scan_id)
print(f"Scan status: {status['status']}")

# Wait for completion
final_status = client.wait_for_completion(scan_id)

# Get results
results = client.get_scan_results(scan_id)
```

## Command Line Usage

Set environment variables:
```bash
export SPIDERFOOT_URL="http://localhost:5001"
export SPIDERFOOT_USERNAME="admin"
export SPIDERFOOT_PASSWORD="your_password"
```

Commands:
```bash
# Test connectivity
spiderfoot-client ping

# Start a scan
spiderfoot-client start example.com "My Scan" --usecase passive

# List all scans
spiderfoot-client list

# Get scan status
spiderfoot-client status SCAN_ID

# Get scan results
spiderfoot-client results SCAN_ID

# Stop a scan
spiderfoot-client stop SCAN_ID

# Delete a scan
spiderfoot-client delete SCAN_ID

# Export results
spiderfoot-client export SCAN_ID --format json

# Wait for scan completion
spiderfoot-client wait SCAN_ID

# Get available modules
spiderfoot-client modules

# Search results
spiderfoot-client search "query" --scan-id SCAN_ID
```

## Configuration

The client can be configured using environment variables:

- `SPIDERFOOT_URL`: SpiderFoot server URL (default: http://localhost:5001)
- `SPIDERFOOT_USERNAME`: Username for authentication (default: admin)
- `SPIDERFOOT_PASSWORD`: Password for authentication (required)

## Requirements

- Python 3.8+
- requests>=2.31.0

## License

MIT License