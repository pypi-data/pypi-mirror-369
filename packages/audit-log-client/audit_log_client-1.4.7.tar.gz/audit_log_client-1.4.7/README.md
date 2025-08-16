# Audit Log Client

Python client for interacting with audit logging services, supporting both synchronous and asynchronous usage.

## Features

- **Dual Mode**: Sync and Async APIs
- **Buffering**: Configurable memory buffering
- **Retry Mechanism**: Exponential backoff retries
- **Fallback Strategy**: Local file storage on failure
- **Query Support**: Flexible log querying capabilities

## Installation

```bash
pip install audit-log-client
```

## Quick Start

### Synchronous Client

```python
from audit_log_client import SyncAuditLogClient, AuditLog, AuditAction, AuditTarget

client = SyncAuditLogClient(
    base_url="http://audit.service/api",
    api_key="your-api-key"
)

log = AuditLog(
    action=AuditAction.UPDATE,
    target_type=AuditTarget.USER,
    user_id="admin",
    description="User profile updated",
    before={"name": "John"},
    after={"name": "John Doe"}
)

client.log(log)
client.close()
```

### Asynchronous Client

```python
import asyncio
from audit_log_client import AsyncAuditLogClient, AuditLog, AuditAction, AuditTarget

async def main():
    client = AsyncAuditLogClient(
        base_url="http://audit.service/api",
        api_key="your-api-key"
    )
    await client.initialize()
    
    log = AuditLog(
        action=AuditAction.CREATE,
        target_type=AuditTarget.ORDER,
        user_id="sales",
        description="New order created"
    )
    
    await client.log(log)
    await client.shutdown()

asyncio.run(main())
```

## Documentation

Full documentation available at [GitHub Wiki](https://github.com/yourusername/audit-log-client/wiki)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)