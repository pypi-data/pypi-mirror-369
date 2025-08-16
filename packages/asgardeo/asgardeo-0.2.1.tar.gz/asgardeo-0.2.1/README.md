# Asgardeo SDK

Simple async Python SDK for Asgardeo authentication.

## Installation

```bash
pip install asgardeo
```



## Quick Start

```python
from asgardeo import AsgardeoConfig, AsgardeoNativeAuthClient

# Setup
config = AsgardeoConfig(
    base_url="https://api.asgardeo.io/t/your-organization",
    client_id="your_client_id",
    redirect_uri="your_redirect_uri",
    client_secret="your_client_secret"  # Optional
)

# Authenticate
async with AsgardeoNativeAuthClient(config) as client:
    # Start flow
    init_response = await client.authenticate()
    
    # Complete with credentials
    auth_response = await client.authenticate(
        authenticator_id="BasicAuthenticator",
        params={"username": "user@example.com", "password": "password"}
    )
    
    # Get tokens
    if client.flow_status == "SUCCESS":
        tokens = await client.get_tokens()
        print(f"Access Token: {tokens.access_token}")
```

## Features

- **Async/await support** - Non-blocking operations
- **Auto resource cleanup** - Context manager support
- **Simple API** - One-line authentication
- **Error handling** - Meaningful exceptions
- **Type hints** - Full type support

## Requirements

- Python >= 3.10
- httpx (async HTTP client)

## Development

```bash
# Install dependencies
poetry install

# Build
poetry build
```

## License

MIT License
