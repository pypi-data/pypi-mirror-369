# Python module Gitlab Parser

## Installation

```bash
pip install GitlabParser
```

## Usage

```
from GitlabParser import Logger

Logger = Logger()
logger = Logger.config()
if Logger.LOG_FILE:
    print(f"See log here: {Logger.LOG_FILE}")
```
