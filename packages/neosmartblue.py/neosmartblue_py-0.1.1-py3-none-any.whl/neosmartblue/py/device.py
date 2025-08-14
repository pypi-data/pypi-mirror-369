import asyncio
from bleak import BleakClient
from .parse_status import parse_status_data

from .const import _RX_UUID, _TX_UUID
from .generate_commands import (
    generate_move_command,
    generate_stop_command,
    generate_status_update_command,
    generate_jog_command,
    generate_ping_command,
)

class BlueLinkDevice:
    """
    A class for communicating with a BlueLink BLE device (Neo Smart Blinds).
    
    This class uses the Nordic UART Service (NUS) to send commands and receive notifications.
    """
    def __init__(self, address: str):
        """
        Initialize the BlueLink device with the given BLE address.
        
        Parameters:
            address (str): The BLE MAC address of the device.
        """
        self.address = address
        self.client = BleakClient(address)
    
    async def connect(self):
        """
        Connect to the BlueLink device.
        """
        await self.client.connect()
        print("Connected to BlueLink device at", self.address)
    
    async def disconnect(self):
        """
        Disconnect from the BlueLink device.
        """
        await self.client.disconnect()
        print("Disconnected from BlueLink device")
    
    async def send_command(self, command: bytes):
        """
        Send a command to the device using the RX characteristic.
        
        Parameters:
            command (bytes): The BLE command payload.
        """
        await self.client.write_gatt_char(_RX_UUID, command)
        print("Sent command:", command.hex().upper())
    
    async def move_to_position(self, position: int):
        """
        Move the blinds to a new position.
        
        Parameters:
            position (int): The target position (0 for fully open, 100 for fully closed).
        """
        command = generate_move_command(position)
        await self.send_command(command)
    
    async def stop(self):
        """
        Immediately stop any ongoing motor movement.
        """
        command = generate_stop_command()
        await self.send_command(command)
    
    async def request_status_update(self):
        """
        Request an updated status report from the device.
        """
        command = generate_status_update_command()
        await self.send_command(command)
    
    async def jog(self):
        """
        Initiate a short jog movement.
        """
        command = generate_jog_command()
        await self.send_command(command)
    
    async def ping(self):
        """
        Send a keep-alive ping command to maintain the BLE connection.
        """
        command = generate_ping_command()
        await self.send_command(command)
    
    async def receive_data(self, timeout: float = 5.0) -> bytes:
        """
        Listen for a notification on the TX characteristic.
        
        Parameters:
            timeout (float): The number of seconds to wait for a notification.
            
        Returns:
            bytes: The data received, or None if no data is received within the timeout.
        """
        data = None

        def notification_handler(sender: int, received_data: bytes):
            nonlocal data
            print("Notification from", sender, ":", received_data.hex().upper())
            # extract the status payload from the received data
            status_payload = received_data[4:9]
            status = parse_status_data(status_payload)
            data = status
            print("Parsed status:", status)

        await self.client.start_notify(_TX_UUID, notification_handler)
        await asyncio.sleep(timeout)
        await self.client.stop_notify(_TX_UUID)
        return data
