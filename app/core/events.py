from PySide6.QtCore import QObject, Signal

class EventBus(QObject):
    # Log Signals
    log_emitted = Signal(str, str, str)  # timestamp, level, message

    # Account Signals
    account_added = Signal(dict)
    account_removed = Signal(int)

    # Contact Signals
    contacts_imported = Signal(int)
    contact_updated = Signal(int)

    # Campaign Signals
    campaign_status_changed = Signal(int, str)  # campaign_id, status
    campaign_progress = Signal(dict)           # stats dictionary
    email_sent = Signal(dict)               # recipient result
    email_failed = Signal(dict)             # recipient failure details

    # Stats Refreshed
    stats_updated = Signal()

# Global Event Bus Singleton
event_bus = EventBus()
