from GitlabParser import __version__
from GitlabParser import Logger

Logger = Logger()
logger = Logger.config(verbose=True)
logger.info(f"Test logger version {__version__}")
if Logger.LOG_FILE:
    print(f"See log here: {Logger.LOG_FILE}")
