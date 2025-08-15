import sys
import signal
from .keyboard_tracker import KeyboardTracker

def main():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Initialize and start keyboard tracker
    tracker = KeyboardTracker()
    tracker.start()

if __name__ == "__main__":
    main()
