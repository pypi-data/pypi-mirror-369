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

async def handle_message(ros_message):
    """Handle incoming ROS messages"""
    if not ros_message:
        return
        
    topic = ros_message.get('topic')
    if not topic:
        return

    print(f'Received ROS message on topic: {topic}')

    # Handle 2d camera messages
    if topic == '/camera2d':
        data = ros_message.get('data', {})
        if data and 'data' in data:
            print(f"Base64 image string: {data['base64Image']}")


    # Handle 3d realsense camera messages
    if topic == '/camera/camera/color/image_raw/compressed':
        data = ros_message.get('data')
        if data:
            print(f"Received 3d camera frame")
            print(f"Base64 image data: {data}")
        else:
            print("No base64 image data found in message")


async def main():
    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(cleanup()))
    
    try:
        # Connect to robotics.dev
        await robotics.connect({
            'server': 'wss://robotics.dev',
            # 'server': 'ws://localhost:3001',
            'robot': '532f2c9f-df66-4d13-b62d-c872703e5448',
            'token': '5a66b323-b464-4d50-9169-77a95014f339'
        }, handle_message)

        print("Listening for ROS messages...")
        
        # Keep the script running
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
