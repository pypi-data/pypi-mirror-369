import threading
import time
from typing import Any, Callable, List, Optional

import zenoh

# A single Zenoh session for the entire process
_session: Optional[zenoh.Session] = None


def _get_session() -> zenoh.Session:
    """Initializes and returns a global Zenoh session."""
    global _session
    if _session is None:
        print("Opening Zenoh session...")
        conf = zenoh.Config()
        _session = zenoh.open(conf)
    return _session


def _shutdown_session() -> None:
    """Closes the global Zenoh session."""
    global _session
    if _session is not None:
        print("Closing Zenoh session...")
        _session.close()
        _session = None


class _Publisher:
    """Internal Publisher class using Zenoh."""

    def __init__(self, session: zenoh.Session, topic: str, msg_type: type) -> None:
        self.session = session
        self.key = topic
        self.msg_type = msg_type
        self.publisher = session.declare_publisher(topic)

    def publish(self, msg: Any) -> None:
        """Serializes and publishes a message."""
        assert isinstance(msg, self.msg_type), (
            f"Message type mismatch! Publisher for '{self.key}' expects "
            f"'{self.msg_type.__name__}' but got '{type(msg).__name__}'"
        )
        buf: bytes = msg.dumps()
        self.publisher.put(buf)


class _Subscriber:
    """Internal Subscriber class using Zenoh."""

    def __init__(
        self,
        session: zenoh.Session,
        topic: str,
        msg_type: type,
        callback: Callable[[Any], None],
    ) -> None:
        self.session = session
        self.key = topic
        self.msg_type = msg_type
        self.user_callback = callback
        self.subscriber = session.declare_subscriber(topic, self._internal_callback)

    def _internal_callback(self, sample: zenoh.Sample) -> None:
        """Internal handler that receives Zbytes from Zenoh and deserializes it."""
        try:
            msg = self.msg_type.loads(sample.payload.to_bytes())
            self.user_callback(msg)
        except Exception as e:
            print(f"Error deserializing message on topic '{self.key}': {e}")


class _RepeatingTimer(threading.Thread):
    """A timer thread that calls a function at regular intervals."""

    def __init__(
        self, interval: float, function: Callable, args=None, kwargs=None
    ) -> None:
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.stop_event = threading.Event()
        self.daemon = True  # Allow thread

    def run(self) -> None:
        """The main loop of the timer thread."""
        while not self.stop_event.wait(self.interval):
            self.function(*self.args, **self.kwargs)

    def stop(self) -> None:
        """Stops the timer thread."""
        self.stop_event.set()


class Node:
    """The main user-facing class for creating publishers and subscribers."""

    def __init__(self, node_name: str) -> None:
        self.name = node_name
        self.session = _get_session()
        self._timers: List[_RepeatingTimer] = []

    def __enter__(self) -> "Node":
        return self

    def __exit__(self, exc_type, exc_value, exec_tb) -> None:
        self.shutdown()

    def create_publisher(self, topic: str, msg_type: type) -> _Publisher:
        print(
            f"Node '{self.name}' creating publisher for topic '{topic}' with type"
            f" '{msg_type.__name__}'."
        )
        return _Publisher(self.session, topic, msg_type)

    def create_subscriber(
        self, topic: str, msg_type: type, callback: Callable[[Any], None]
    ) -> _Subscriber:
        print(
            f"Node '{self.name}' creating subscription for topic '{topic}' with type"
            f" '{msg_type.__name__}'."
        )
        return _Subscriber(self.session, topic, msg_type, callback)

    def create_timer(
        self, period_sec: float, callback: Callable, *args, **kwargs
    ) -> None:
        timer = _RepeatingTimer(period_sec, callback, args=args, kwargs=kwargs)
        self._timers.append(timer)
        timer.start()

    def spin(self) -> None:
        """Blocks execution to process callbacks until a KeyboardInterrupt (Ctrl+C)."""
        try:
            while True:
                time.sleep(1)  # Sleep to prevent high CPU usage
        except KeyboardInterrupt:
            print("\nReceiving keyboard interrupt...")

    def shutdown(self) -> None:
        """Shuts down the node and closes the Zenoh session."""
        print(f"Shutting down node '{self.name}'...")
        for timer in self._timers:
            timer.stop()
        _shutdown_session()
