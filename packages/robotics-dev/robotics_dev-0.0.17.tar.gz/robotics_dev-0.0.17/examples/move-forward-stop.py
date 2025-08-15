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
    # print('Received p2p data:', ros_message)

    # Only proceed if we have a connected message
    if ros_message.get('type') == 'connected':
        print('Connection established, waiting for channels to be ready...')
        await asyncio.sleep(2)  # Give channels time to open
        
        if one_time:
            one_time = False
            # await asyncio.sleep(5)
            print('Sending test message...')
            await robotics.speak('532f2c9f-df66-4d13-b62d-c872703e5448', 'this is a test')

            print('Moving robot forward at 20% speed...')
            await robotics.twist('532f2c9f-df66-4d13-b62d-c872703e5448', forward_twist)

            # Stop after 5 seconds
            await asyncio.sleep(5)
            print('Stopping robot...')
            await robotics.twist('532f2c9f-df66-4d13-b62d-c872703e5448', stop_twist)
            await robotics.speak('532f2c9f-df66-4d13-b62d-c872703e5448', 'thats all folks')

async def main():
    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup()))

    try:
        # Connect to robotics.dev
        await robotics.connect({
            'server': 'ws://192.168.0.145:3001',
            'robot': '532f2c9f-df66-4d13-b62d-c872703e5448',
            'token': '5a66b323-b464-4d50-9169-77a95014f339'
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
