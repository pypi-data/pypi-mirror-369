import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.rtcconfiguration import RTCConfiguration, RTCIceServer
import socketio
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List
import uuid
import base64
import numpy as np
import cv2
import sys
import struct

class RoboticsClient:
    def __init__(self):
        self._pc: Optional[RTCPeerConnection] = None
        self._channels: Dict[int, Any] = {}  # Map to store multiple data channels
        self._current_channel_index = 0
        self._num_channels = 10  # Default number of data channels
        self._sio = None
        self._connected = False
        self._callback = None
        self._robot_id = None
        self._token = None
        self._pending_messages = []
        self.messages = {}
        self._setup_complete = False
        self._setup_in_progress = False
        self._has_remote_description = False
        self._pending_candidates = []
        self._max_message_size = 16384  # Match JavaScript maxMessageSize
        self._port_range_begin = 5000  # Match JavaScript portRangeBegin
        self._port_range_end = 6000  # Match JavaScript portRangeEnd
        self._channel_recreation_times = {}  # Track when channels were last recreated
        self._min_recreation_delay = 5  # Minimum seconds between recreations

    def _get_next_channel(self) -> Optional[Any]:
        """Get next available channel in round-robin fashion"""
        if not self._channels:
            return None
        channel = self._channels.get(self._current_channel_index)
        self._current_channel_index = (self._current_channel_index + 1) % self._num_channels
        return channel

    async def _send_compressed_message(self, message: Dict[str, Any]) -> None:
        """Send message through available channels"""
        try:
            print(f"\n=== Sending Message ===")
            print(f"Message: {json.dumps(message, indent=2)}")
            
            # Validate message format
            if not isinstance(message, dict):
                print("ERROR: Message must be a dictionary")
                return
                
            # Check for P2P message format
            if 'type' in message:
                print(f"Sending P2P message of type: {message['type']}")
            else:
                # Validate ROS message format
                if 'topic' not in message:
                    print("ERROR: Message must have a topic")
                    return
                    
                if message['topic'] == 'speak' and not isinstance(message.get('text'), str):
                    print("ERROR: Speak message must have text as string")
                    return
                    
                if message['topic'] == 'twist' and not isinstance(message.get('twist'), dict):
                    print("ERROR: Twist message must have twist as dictionary")
                    return
            
            # Convert message to JSON string
            message_str = json.dumps(message)
            message_id = str(uuid.uuid4())
            chunk_size = self._max_message_size
            total_chunks = (len(message_str) + chunk_size - 1) // chunk_size

            # Get all open channels
            open_channels = [
                channel for channel in self._channels.values()
                if channel and channel.readyState == "open"
            ]
            
            print(f"Open channels: {len(open_channels)}")
            print(f"Channel states: {[(i, ch.readyState) for i, ch in self._channels.items()]}")
            
            if not open_channels:
                print("No open channels available")
                self._pending_messages.append(message)
                return

            print(f"Sending {total_chunks} chunks for message {message_id}")
            print(f"Total channels available: {len(open_channels)}")

            # Distribute chunks across all available channels
            for i in range(total_chunks):
                chunk = message_str[i * chunk_size:(i + 1) * chunk_size]
                # Create message chunk format to match JavaScript exactly
                message_chunk = {
                    'chunk': chunk,
                    'index': i,
                    'total': total_chunks,
                    'messageId': message_id
                }
                
                # Select channel based on chunk index
                channel_index = i % len(open_channels)
                channel = open_channels[channel_index]
                
                try:
                    print(f"Sending chunk {i + 1}/{total_chunks} on channel {channel.label}")
                    print(f"Channel state: {channel.readyState}")
                    # Send as string that can be parsed by JSON.parse()
                    message_str = json.dumps(message_chunk)
                    print(f"Sending message: {message_str}")
                    channel.send(message_str)
                    print(f"Successfully sent chunk {i + 1}/{total_chunks}")
                except Exception as e:
                    print(f"Error sending chunk {i + 1}/{total_chunks} on channel {channel.label}: {e}")
                    self._pending_messages.append(message_chunk)

        except Exception as e:
            print(f"Error sending message: {e}")
            self._pending_messages.append(message)

    async def _setup_peer_connection(self):
        """Set up WebRTC peer connection with multiple data channels"""
        if self._setup_in_progress:
            print("Setup already in progress, skipping...")
            return
        
        self._setup_in_progress = True
        print("\n=== Setting up Peer Connection ===")
        print(f"Current connection state: {self._pc.connectionState if self._pc else 'No PC'}")
        print(f"Current ICE connection state: {self._pc.iceConnectionState if self._pc else 'No PC'}")
        
        try:
            if self._pc:
                print("Closing existing peer connection...")
                await self._pc.close()
                self._pc = None

            # Match JavaScript configuration
            config = RTCConfiguration([
                RTCIceServer(urls=["stun:stun1.l.google.com:19302"]),
                RTCIceServer(urls=["stun:stun2.l.google.com:19302"])
            ])
            
            # Set port range and max message size
            config.portRangeBegin = self._port_range_begin
            config.portRangeEnd = self._port_range_end
            config.maxMessageSize = self._max_message_size
            
            print("Creating new peer connection...")
            self._pc = RTCPeerConnection(configuration=config)

            @self._pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print(f"\n=== Connection State Changed ===")
                print(f"New state: {self._pc.connectionState}")
                print(f"ICE connection state: {self._pc.iceConnectionState}")
                print(f"ICE gathering state: {self._pc.iceGatheringState}")
                if self._pc.connectionState == "connected":
                    print("Peer connection established!")
                    self._connected = True
                    self._setup_complete = True
                    self._setup_in_progress = False
                    print(f"Active data channels: {[(i, ch.readyState) for i, ch in self._channels.items()]}")
                    open_channels = [ch for ch in self._channels.values() if ch and ch.readyState == "open"]
                    print(f"Total open channels: {len(open_channels)}/{self._num_channels}")
                    if len(open_channels) == 0:
                        print("WARNING: No open channels after connection established!")

            @self._pc.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                print(f"\n=== ICE Connection State Changed ===")
                print(f"New state: {self._pc.iceConnectionState}")

            @self._pc.on("icegatheringstatechange")
            async def on_icegatheringstatechange():
                print(f"\n=== ICE Gathering State Changed ===")
                print(f"New state: {self._pc.iceGatheringState}")

            # Create data channels
            print("\n=== Creating Data Channels ===")
            for i in range(self._num_channels):
                try:
                    channel = self._pc.createDataChannel(
                        f'robotics-{i}',
                        ordered=True,
                        protocol='chat'
                    )
                    self._channels[i] = channel
                    print(f"Created data channel {i}: {channel.label}")
                    print(f"Channel ID: {channel.id}")
                    print(f"Initial State: {channel.readyState}")
                    self._setup_data_channel(channel)
                except Exception as e:
                    print(f"Error creating data channel {i}: {e}")
                    raise e

            # Create and send offer
            print("\n=== Creating Offer ===")
            offer = await self._pc.createOffer()
            await self._pc.setLocalDescription(offer)

            # Format SDP for compatibility
            sdp_lines = []
            ice_lines = []
            fingerprint = None

            # Extract components from original SDP
            for line in offer.sdp.split('\r\n'):
                if line.startswith('a=ice-ufrag:'):
                    ice_lines.append(line)
                elif line.startswith('a=ice-pwd:'):
                    ice_lines.append(line)
                elif line.startswith('a=fingerprint:sha-256'):
                    fingerprint = line

            # Build SDP with exact format
            sdp_lines = [
                'v=0',
                f'o=- {int(datetime.now().timestamp())} 1 IN IP4 0.0.0.0',
                's=-',
                't=0 0',
                'm=application 9 UDP/DTLS/SCTP webrtc-datachannel',
                'c=IN IP4 0.0.0.0',
                'a=mid:0'
            ]

            # Add ICE and fingerprint in correct order
            sdp_lines.extend(ice_lines)
            if fingerprint:
                sdp_lines.append(fingerprint)

            # Add required attributes
            sdp_lines.extend([
                'a=sctp-port:5000',
                'a=max-message-size:262144',
                'a=setup:actpass'
            ])

            modified_sdp = '\r\n'.join(sdp_lines) + '\r\n'

            # Send offer
            print("\n=== Sending Offer ===")
            await self._sio.emit('signal', {
                'type': 'offer',
                'robot': self._robot_id,
                'token': self._token,
                'targetPeer': self._robot_id,
                'sourcePeer': self._client_id,
                'room': self._robot_id,
                'sdp': modified_sdp
            })
            print("Sent offer to peer")

            @self._pc.on("icecandidate")
            async def on_icecandidate(candidate):
                if candidate:
                    print(f"\n=== ICE Candidate ===")
                    print(f"Candidate: {candidate.candidate}")
                    await self._sio.emit('signal', {
                        'type': 'candidate',
                        'robot': self._robot_id,
                        'token': self._token,
                        'targetPeer': self._robot_id,
                        'sourcePeer': self._client_id,
                        'room': self._robot_id,
                        'candidate': candidate.candidate,
                        'mid': candidate.sdpMid
                    })

        except Exception as e:
            print(f"Setup failed: {e}")
            self._setup_in_progress = False
            raise e

    async def _handle_peer_reply(self, data):
        """Handle peer connection signaling"""
        try:
            print(f"\n=== Handling Peer Reply ===")
            print(f"Type: {data.get('type')}")
            
            if data['type'] == 'answer':
                # Convert answer SDP for aiortc
                sdp = data['sdp'].replace(
                    'UDP/DTLS/SCTP webrtc-datachannel',
                    'DTLS/SCTP 5000'
                )
                answer = RTCSessionDescription(sdp=sdp, type='answer')
                await self._pc.setRemoteDescription(answer)
                self._has_remote_description = True
                print("Set remote description")
                
                # Process any pending candidates
                while self._pending_candidates:
                    candidate = self._pending_candidates.pop(0)
                    await self._pc.addIceCandidate(candidate)
                    print(f"Added pending ICE candidate: {candidate.candidate}")
                
                # Check data channel states after setting remote description
                print("\n=== Data Channel States After Answer ===")
                for i, channel in self._channels.items():
                    print(f"Channel {i}: {channel.readyState}")
                
                # Wait a bit for channels to open
                await asyncio.sleep(1)
                
                # Check channel states again
                print("\n=== Data Channel States After Delay ===")
                open_channels = []
                for i, channel in self._channels.items():
                    print(f"Channel {i}: {channel.readyState}")
                    if channel.readyState == "open":
                        open_channels.append(channel)
                    else:
                        # Only recreate if enough time has passed
                        current_time = datetime.now().timestamp()
                        last_recreation = self._channel_recreation_times.get(i, 0)
                        if current_time - last_recreation >= self._min_recreation_delay:
                            print(f"Attempting to reopen channel {i}")
                            try:
                                new_channel = self._pc.createDataChannel(
                                    f'robotics-{i}',
                                    ordered=True,
                                    protocol='chat'
                                )
                                self._channels[i] = new_channel
                                self._setup_data_channel(new_channel)
                                self._channel_recreation_times[i] = current_time
                                print(f"Recreated channel {i}")
                                if new_channel.readyState == "open":
                                    open_channels.append(new_channel)
                            except Exception as e:
                                print(f"Error recreating channel {i}: {e}")
            
            elif data['type'] == 'candidate':
                try:
                    # Handle candidate string directly
                    raw = data.get('candidate', '')
                    if raw.startswith('a='):
                        raw = raw[2:]
                    if raw.startswith('candidate:'):
                        raw = raw[10:]
                    
                    # Parse the candidate string
                    parts = raw.split()
                    if len(parts) >= 8:
                        # Create candidate with parsed components
                        candidate = RTCIceCandidate(
                            component=1,
                            foundation=parts[0],
                            protocol=parts[2].lower(),
                            priority=int(parts[3]),
                            ip=parts[4],
                            port=int(parts[5]),
                            type=parts[7],
                            sdpMid=data.get('mid', '0'),
                            sdpMLineIndex=0
                        )
                        
                        if not self._has_remote_description:
                            self._pending_candidates.append(candidate)
                            print(f"Queued ICE candidate: {raw}")
                        else:
                            await self._pc.addIceCandidate(candidate)
                            print(f"Added ICE candidate: {raw}")
                except Exception as e:
                    print(f"ICE candidate error: {str(e)}")
                    print(f"Raw candidate data: {data}")

        except Exception as e:
            print(f"Peer reply error: {str(e)}")
            print(f"Full data: {data}")

    def _convert_compressed_image_to_base64(self, image_data):
        """Convert compressed image data to base64 string"""
        try:
            # Handle different possible data structures
            compressed_data = None
            if isinstance(image_data, list):
                compressed_data = image_data
            elif isinstance(image_data, dict):
                if isinstance(image_data.get('data'), list):
                    compressed_data = image_data['data']
                elif isinstance(image_data.get('buffer'), (list, bytes)):
                    compressed_data = image_data['buffer']
                elif isinstance(image_data.get('data'), dict):
                    # Handle the case where data is an object with numeric keys
                    data_obj = image_data['data']
                    # Convert numeric-keyed object to array
                    compressed_data = [data_obj[str(i)] for i in range(len(data_obj))]
                else:
                    print("Unsupported image data format")
                    return None
            else:
                print("Unsupported image data format")
                return None

            if not compressed_data or len(compressed_data) == 0:
                print("No valid image data found")
                return None
            
            # Convert the array to bytes
            buffer = bytes(compressed_data)
            
            # Convert bytes to base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            
            # Validate the base64 string
            if len(base64_str) < 100:  # Arbitrary minimum length for a valid image
                print("Generated base64 string too short, likely invalid")
                return None
            
            return base64_str
        except Exception as e:
            print(f"Error converting compressed image: {e}")
            return None

    def _setup_data_channel(self, channel):
        """Set up data channel handlers"""
        if not channel:
            print("No channel provided to setup")
            return

        @channel.on("open")
        def on_open():
            print(f"\n=== Data Channel {channel.label} Opened ===")
            print(f"Channel ID: {channel.id}")
            print(f"Channel Protocol: {channel.protocol}")
            print(f"Channel State: {channel.readyState}")
            print(f"Peer Connection State: {self._pc.connectionState if self._pc else 'No PC'}")
            print(f"ICE Connection State: {self._pc.iceConnectionState if self._pc else 'No PC'}")
            
            # Only send ready signal if peer connection is connected
            if self._pc and self._pc.connectionState == "connected":
                # Send ready signal
                ready_msg = json.dumps({
                    "type": "ready",
                    "channel": channel.id,
                    "total_channels": self._num_channels
                })
                print(f"Sending ready signal on channel {channel.id}: {ready_msg}")
                try:
                    # Send as string that can be parsed by JSON.parse()
                    channel.send(ready_msg)
                    print(f"Successfully sent ready signal on channel {channel.id}")
                except Exception as e:
                    print(f"Error sending ready signal on channel {channel.id}: {e}")
                    return
                
                # Execute callback
                if self._callback:
                    print(f"Executing connected callback for channel {channel.id}")
                    asyncio.create_task(self._callback({"type": "connected", "channel": channel.id}))
            else:
                print(f"Not sending ready signal - peer connection not ready: {self._pc.connectionState if self._pc else 'No PC'}")

        @channel.on("message")
        def on_message(message):
            if not self._callback:
                return
                
            try:
                # Handle binary data
                if isinstance(message, (bytes, bytearray)):
                    # Extract header information (matching comms.js format)
                    index = int.from_bytes(message[0:8], byteorder='big')
                    total = int.from_bytes(message[8:16], byteorder='big')
                    message_id = message[16:52].hex()
                    message_id = f"{message_id[0:8]}-{message_id[8:12]}-{message_id[12:16]}-{message_id[16:20]}-{message_id[20:32]}"
                    chunk_data = message[52:].decode('utf-8')

                    # Initialize or get existing message chunks
                    if message_id not in self.messages:
                        self.messages[message_id] = {
                            'chunks': [None] * total,
                            'received': 0,
                            'total': total
                        }
                    
                    message_info = self.messages[message_id]
                    message_info['chunks'][index] = chunk_data
                    message_info['received'] += 1

                    # If all chunks received, process complete message
                    if message_info['received'] == message_info['total']:
                        complete_message = ''.join(message_info['chunks'])
                        try:
                            data_obj = json.loads(complete_message)
                            if data_obj.get('topic'):
                                # Handle camera image messages
                                if data_obj['topic'] == '/camera/camera/color/image_raw/compressed' and data_obj.get('data'):
                                    # base64_image = self._convert_compressed_image_to_base64(data_obj['data'])
                                    # if base64_image:
                                    #     data_obj['data']['base64Image'] = base64_image
                                    pass

                                if data_obj['topic'] == '/camera/camera/color/image_raw' and data_obj.get('data'):
                                    # Base64 image data is already in data_obj['data']
                                    pass

                                if data_obj['topic'] == '/camera/camera/depth/image_rect_raw/compressedDepth' and data_obj.get('data'):
                                    depth = self.calculate_depth(data_obj['data'])
                                    if depth is not None:
                                        data_obj['data']['depth'] = depth

                                if data_obj['topic'] == '/camera2d' and data_obj.get('data'):
                                    data_obj['data']['base64Image'] = data_obj['data']

                                if self._callback:
                                    asyncio.create_task(self._callback(data_obj))
                        except Exception as e:
                            print(f"Error parsing complete message: {e}")
                        del self.messages[message_id]
                else:
                    # Handle legacy string messages
                    if isinstance(message, str):
                        data = json.loads(message)
                    else:
                        data = json.loads(message.decode('utf-8'))

                    # Only process if it's a ROS message with a topic
                    if data.get('topic'):
                        # Skip camera messages as they're handled in binary mode
                        if 'camera' not in data['topic'] and self._callback:
                            asyncio.create_task(self._callback(data))
            except Exception as e:
                print(f"Message handling error: {e}")
                # Try to handle raw message
                if self._callback and isinstance(message, str):
                    asyncio.create_task(self._callback({'data': message}))

        @channel.on("error")
        def on_error(error):
            print(f"\n=== Data Channel {channel.label} Error ===")
            print(f"Channel ID: {channel.id}")
            print(f"Error: {error}")
            self._connected = False

        @channel.on("close")
        def on_close():
            print(f"\n=== Data Channel {channel.label} Closed ===")
            print(f"Channel ID: {channel.id}")
            self._connected = False

    async def disconnect(self) -> None:
        """Clean shutdown of connections"""
        for channel in self._channels.values():
            if channel:
                channel.close()
        self._channels.clear()
        if self._pc:
            await self._pc.close()
        if self._sio:
            await self._sio.disconnect()
        self._connected = False

    async def connect(self, options: Dict[str, str], callback: Callable[[Dict], None]) -> None:
        """Connect to robotics.dev and establish P2P connection"""
        self._callback = callback
        self._robot_id = options.get('robot')
        self._token = options.get('token')
        
        # Ensure server URL is properly handled
        server = options.get('server')
        if not server:
            server = 'wss://robotics.dev'
        elif server.startswith('http://'):
            server = server.replace('http://', 'ws://')
        elif server.startswith('https://'):
            server = server.replace('https://', 'wss://')
        elif not server.startswith(('ws://', 'wss://')):
            server = f"ws://{server}"
            
        self._server = server
        print(f"Using signaling server: {self._server}")

        if not self._robot_id or not self._token:
            raise ValueError("Both robot ID and token are required")

        # Initialize socket.io with debugging
        self._sio = socketio.AsyncClient(logger=True, engineio_logger=True)
        self._client_id = f'remote-{hex(int(datetime.now().timestamp()))[2:]}'

        @self._sio.event
        async def connect():
            print(f"Connected to signaling server: {self._server}")
            print(f"Client ID: {self._client_id}")
            # Emit register event first
            await self._sio.emit('register', {
                'id': self._client_id,
                'room': self._robot_id,
                'token': self._token
            })
            # Then emit join signal
            await self._sio.emit('signal', {
                'type': 'join',
                'robot': self._robot_id,
                'token': self._token,
                'targetPeer': self._robot_id,
                'sourcePeer': self._client_id,
                'room': self._robot_id  # Add room parameter
            })
            # Set up peer connection immediately after registering
            await self._setup_peer_connection()

        @self._sio.event
        async def disconnect():
            print("Disconnected from signaling server")

        @self._sio.event
        async def error(data):
            print(f"Socket.IO error: {data}")

        @self._sio.event
        async def signal(data):
            print(f"Received signal: {data.get('type')}")
            if data.get('type') in ['answer', 'candidate']:
                await self._handle_peer_reply(data)

        @self._sio.event
        async def room_info(info):
            print(f"Received room info: {info}")
            if info.get('peers') and self._robot_id in info['peers'] and not self._connected and not self._setup_complete:
                await self._setup_peer_connection()

        # Connect with proper URL parameters
        connection_url = (
            f"{self._server}?"
            f"id={self._client_id}&"
            f"room={self._robot_id}&"  # Add room parameter
            f"token={self._token}"
        )
        
        print(f"Connecting to: {connection_url}")
        await self._sio.connect(
            connection_url,
            transports=["websocket"],
            auth={'id': self._client_id}  # Add auth parameter
        )

        # Keep the connection alive and wait for messages
        while True:
            try:
                await asyncio.sleep(1)
                # Check if we have any open channels
                open_channels = [ch for ch in self._channels.values() if ch and ch.readyState == "open"]
                if not open_channels and self._connected:
                    print("No open channels, attempting to reconnect...")
                    await self._setup_peer_connection()
            except Exception as e:
                print(f"Error in connection loop: {e}")
                break

    async def twist(self, robot: str, twist_msg: Dict[str, Any]) -> None:
        """Send twist command to robot"""
        print(f"\n=== Sending Twist Command ===")
        print(f"Robot: {robot}")
        print(f"Twist message: {json.dumps(twist_msg, indent=2)}")
        
        # Validate twist message format
        if not isinstance(twist_msg, dict):
            print("ERROR: Twist message must be a dictionary")
            return
            
        # Create message format to match robotics.js exactly
        message = {
            'topic': 'twist',
            'robot': robot,
            'twist': twist_msg
        }
        print(f"Twist message format: {json.dumps(message, indent=2)}")
        await self._send_message(message)

    async def speak(self, robot: str, text: str) -> None:
        """Send speak command to robot"""
        print(f"\n=== Sending Speak Command ===")
        print(f"Robot: {robot}")
        print(f"Text: {text}")
        
        # Validate text format
        if not isinstance(text, str):
            print("ERROR: Text must be a string")
            return
            
        # Create message format to match robotics.js exactly
        message = {
            'topic': 'speak',
            'robot': robot,
            'text': text
        }
        print(f"Speak message format: {json.dumps(message, indent=2)}")
        await self._send_message(message)

    async def _send_message(self, message: Dict[str, Any]) -> None:
        """Send message through data channel or queue if not connected"""
        try:
            print(f"\n=== Sending Message ===")
            print(f"Connected: {self._connected}")
            print(f"Message: {message}")
            
            # Wait for connection to be established
            max_wait = 10  # Maximum seconds to wait
            start_time = datetime.now().timestamp()
            while not self._connected or not self._pc or self._pc.connectionState != "connected":
                if datetime.now().timestamp() - start_time > max_wait:
                    print("Timeout waiting for connection")
                    self._pending_messages.append(message)
                    return
                print("Waiting for connection to be established...")
                await asyncio.sleep(0.5)
            
            # Wait for at least one channel to be open
            while not any(ch and ch.readyState == "open" for ch in self._channels.values()):
                if datetime.now().timestamp() - start_time > max_wait:
                    print("Timeout waiting for open channel")
                    self._pending_messages.append(message)
                    return
                print("Waiting for channel to open...")
                await asyncio.sleep(0.5)
            
            if self._connected:
                print("Sending through data channel...")
                # For speak and twist messages, send directly without compression
                if message.get('topic') in ['speak', 'twist']:
                    # Get an open channel
                    open_channels = [ch for ch in self._channels.values() if ch and ch.readyState == "open"]
                    if open_channels:
                        channel = open_channels[0]  # Use first open channel
                        try:
                            print(f"Sending direct message on channel {channel.label}")
                            print(f"Channel state: {channel.readyState}")
                            message_str = json.dumps(message)
                            print(f"Sending message: {message_str}")
                            channel.send(message_str)
                            print(f"Successfully sent direct message")
                        except Exception as e:
                            print(f"Error sending direct message on channel {channel.label}: {e}")
                            self._pending_messages.append(message)
                    else:
                        print("No open channels available")
                        self._pending_messages.append(message)
                else:
                    # For other messages, use compression
                    await self._send_compressed_message(message)
            else:
                print("Not connected, queueing message")
                self._pending_messages.append(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            self._pending_messages.append(message)

    # RealSense D435 specific constants
    DEPTH_WIDTH = 424  # Fixed width for RealSense D435
    DEPTH_HEIGHT = 240  # Fixed height for RealSense D435
    MIN_DEPTH = 100    # 100mm minimum depth
    MAX_DEPTH = 10000  # 10000mm maximum depth
    DEPTH_SCALE = 1.5  # Scale factor to correct depth values

    # PNG signature bytes
    PNG_SIGNATURE = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])

    def calculate_depth(self, depth_data):
        """Calculate depth from compressed depth data"""
        try:
            if not depth_data or not depth_data.get('data'):
                print("No depth data received")
                return None

            # Convert the raw data to bytes
            raw_data = list(depth_data['data'].values())
            buffer = bytes(raw_data)
            
            # Find the PNG signature in the buffer
            png_start = buffer.find(self.PNG_SIGNATURE)
            if png_start == -1:
                print("PNG signature not found in data")
                return None
            
            # Extract the PNG data starting from the signature
            png_data = buffer[png_start:]
            
            # Decode the PNG data
            depth_image = cv2.imdecode(np.frombuffer(png_data, np.uint8), cv2.IMREAD_UNCHANGED)
            if depth_image is None:
                print("Failed to decode depth image")
                return None

            # Create a 2D array for depth values
            depth_values = np.zeros((self.DEPTH_HEIGHT, self.DEPTH_WIDTH), dtype=np.uint16)
            valid_count = 0
            
            # Read depth values from image data
            for y in range(min(depth_image.shape[0], self.DEPTH_HEIGHT)):
                for x in range(min(depth_image.shape[1], self.DEPTH_WIDTH)):
                    if len(depth_image.shape) == 3:  # RGB/RGBA image
                        # Read 16-bit value (little-endian)
                        raw_value = (depth_image[y, x, 1] << 8) | depth_image[y, x, 0]
                    else:  # Grayscale image
                        raw_value = depth_image[y, x]
                    
                    # Apply scaling factor to get correct depth
                    value = int(raw_value * self.DEPTH_SCALE)
                    
                    # Store the value
                    depth_values[y, x] = value
                    if self.MIN_DEPTH <= value <= self.MAX_DEPTH:
                        valid_count += 1

            # Calculate center coordinates
            center_x = self.DEPTH_WIDTH // 2
            center_y = self.DEPTH_HEIGHT // 2
            
            # Get the center pixel value
            center_depth = depth_values[center_y, center_x]
            
            # Return depth in meters if valid, otherwise None
            if self.MIN_DEPTH <= center_depth <= self.MAX_DEPTH:
                return center_depth / 1000.0
            return None

        except Exception as e:
            print(f"Error calculating depth: {e}")
            return None

# Create singleton instance
robotics = RoboticsClient()
