import signal
import sys

def signal_handler(sig, frame):
    print(f"SIGNAL RECEIVED: {sig}")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
