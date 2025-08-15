# ROBOTICS.DEV App Builder

Run P2P AI Robotics.dev apps anywhere!

````
pip install robotics-dev
````

Usage:

````
await robotics.connect({
    'server': 'ws://192.168.0.47:3001',
    'robot': 'eeeaa722-...-9a53-c945a5822b60',
    'token': '5a66b323-...-9169-77a95014f339'
}, handle_message)

robotics.speak('eeeaa722-...-9a53-c945a5822b60', 'this is a test')

robotics.twist('eeeaa722-...-9a53-c945a5822b60', forward_twist)
````

Here's an example python script: 
````
import asyncio
import signal
import base64
import sys
from pathlib import Path

# Add the src directory to Python path for local testing
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

# Import for local testing
from robotics_dev.robotics import robotics
# For production, use:
# from robotics_dev import robotics

# Create twist message for moving forward at 20% speed
forward_twist = {
    "linear": {
        "x": 0.2,  # 20% forward velocity
        "y": 0.0,
        "z": 0.0
    },
    "angular": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    }
}

# Create stop twist message
stop_twist = {
    "linear": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    },
    "angular": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    }
}

one_time = True

async def handle_message(ros_message):
    global one_time
    # ros_message is already parsed by the SDK
    print('Received p2p data:', ros_message)

    if one_time:
        one_time = False
        await robotics.speak('eeeaa722-...-9a53-c945a5822b60', 'this is a test')

        print('Moving robot forward at 20% speed...')
        await robotics.twist('eeeaa722-...-9a53-c945a5822b60', forward_twist)

        # Stop after 5 seconds
        await asyncio.sleep(5)
        print('Stopping robot...')
        await robotics.twist('eeeaa722-...-9a53-c945a5822b60', stop_twist)

async def main():
    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup()))

    try:
        # Connect to robotics.dev
        await robotics.connect({
            'server': 'ws://192.168.0.47:3001',
            'robot': 'eeeaa722-...-9a53-c945a5822b60',
            'token': '5a66b323-...-9169-77a95014f339'
        }, handle_message)

        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print("Shutdown requested...")
    except Exception as e:
        print(f"Error: {e}")

async def cleanup():
    print("Disconnecting...")
    await robotics.disconnect()
    # Stop the event loop
    loop = asyncio.get_running_loop()
    loop.stop()

if __name__ == "__main__":
    asyncio.run(main())
````
