# 03.05.2025

import os
import sys
import threading
import asyncio
import subprocess  # Added for restart


def restart_script():
    """Restarts the script with the same command-line arguments."""
    print("\nRestarting the script...\n")
    python = sys.executable
    # Use subprocess.Popen for better control potentially, or stick with os.execv
    # os.execv(python, [python] + sys.argv)
    try:
        # Using Popen allows the current process to exit cleanly first
        subprocess.Popen([python] + sys.argv)
        sys.exit(0)  # Exit the current process
    except Exception as e:
        print(f"Error restarting script: {e}")
        force_exit()  # Fallback to force exit if restart fails


def force_exit():
    """Forces the script to close in any context."""
    print("\nClosing the script...")

    # 1 Close all threads except the main one
    main_thread = threading.main_thread()
    for t in threading.enumerate():
        if t is not main_thread:
            print(f"Attempting to join thread: {t.name}")
            try:
                # Give threads a chance to finish, but don't wait indefinitely
                t.join(timeout=0.5)
                if t.is_alive():
                    print(f"Thread {t.name} did not exit cleanly.")
            except Exception as e:
                print(f"Error joining thread {t.name}: {e}")

    # 2 Stop asyncio event loop if running
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            print("Stopping asyncio loop...")
            loop.call_soon_threadsafe(loop.stop)
            # Give loop a moment to process stop()
            # This part is tricky and might depend on the asyncio usage
    except RuntimeError:  # No running loop
        pass
    except Exception as e:
        print(f"Error stopping asyncio loop: {e}")

    # 3 Exit forcefully
    print("Forcing exit with os._exit(0)")
    os._exit(0)  # Use os._exit for immediate termination without cleanup

