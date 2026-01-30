import logging
from collections import defaultdict

class EventBus:
    """
    A simple centralized event bus for decoupled communication.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = defaultdict(list)
        return cls._instance

    def subscribe(self, event_type, callback):
        """
        Subscribe a callback to an event type.
        """
        self._subscribers[event_type].append(callback)
        # logging.debug(f"Subscribed to {event_type}: {callback}")

    def unsubscribe(self, event_type, callback):
        """
        Unsubscribe a callback from an event type.
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass

    def publish(self, event_type, data=None):
        """
        Publish an event to all subscribers.
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logging.error(f"Error handling event {event_type}: {e}")
