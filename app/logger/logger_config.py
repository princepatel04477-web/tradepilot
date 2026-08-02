import sys
import logging
from pathlib import Path
from loguru import logger
from app.core.constants import LOGS_DIR
from app.core.events import event_bus

class QtLogSink:
    """Redirects loguru messages to PySide6 EventBus for UI streaming."""
    def write(self, message):
        record = message.record
        timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
        level = record["level"].name
        text = record["message"]
        event_bus.log_emitted.emit(timestamp, level, text)

class InterceptHandler(logging.Handler):
    """Intercept standard logging calls and route to Loguru."""
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logger():
    logger.remove()
    
    # Console Sink
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="INFO")
    
    # Log File Sink
    log_file = LOGS_DIR / "tradepilot.log"
    logger.add(log_file, rotation="10 MB", retention="30 days", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}")
    
    # Qt UI Sink
    qt_sink = QtLogSink()
    logger.add(qt_sink.write, level="INFO")
    
    # Hook Python standard logging (e.g. googleapiclient) to loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    logger.info("TradePilot logger initialized.")

setup_logger()
