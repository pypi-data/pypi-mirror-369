# global_service

A Python package for global logging, step-wise logging, and Oracle DB activity logging, with robust log delivery and local fallback.

## Features
- Centralized logging to a global service (HTTP endpoint)
- Step-wise logger for tracking process steps
- Oracle DB logging for web activity
- Local fallback for failed log delivery
- Fully dynamic configuration via code or environment variables

## Installation

```powershell
pip install global-service
```

## Usage

```python
from global_service import config, build_global_log_payload, send_log_to_global_service, StepLogger, save_step_logs_to_oracle

# Configure dynamically (recommended)
config.configure(
    GLOBAL_LOG_URL="http://your-log-server:8000/web_logs",
    APP_CODE="MY-APP-CODE",
    ORACLE_DB_HOST="dbhost",
    ORACLE_DB_PORT=1521,
    ORACLE_DB_SERVICE="ORCLPDB",
    ORACLE_USER="user",
    ORACLE_PASS="pass"
)

# Example: Send a log
payload = build_global_log_payload(request)
send_log_to_global_service(payload)

# Example: Step logger
step_logger = StepLogger()
step_logger.log("Step 1: Started")
step_logger.log("Step 2: Processing")
# ...
save_step_logs_to_oracle(payload, step_logger, request_body, response_body)
```

## License

MIT License

Copyright (c) 2024 [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

