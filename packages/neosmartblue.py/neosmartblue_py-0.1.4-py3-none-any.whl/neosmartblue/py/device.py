import asyncio
import logging
from typing import Optional, Dict, Any
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
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
    
    async def receive_data(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Listen for a notification on the TX characteristic.

        Parameters:
            timeout (float): The number of seconds to wait for a notification.

        Returns:
            Optional[Dict[str, Any]]: Parsed status dict from parse_status_data, or None if timeout/no notification.
        """
        logger = logging.getLogger(__name__)
        data: Optional[Dict[str, Any]] = None
        data_event = asyncio.Event()

        def notification_handler(sender: BleakGATTCharacteristic, received_data: bytearray):
            nonlocal data
            try:
                printable = bytes(received_data)
                logger.info(
                    "Notification from characteristic %s: %s",
                    getattr(sender, 'uuid', sender),
                    printable.hex().upper(),
                )
                if len(printable) >= 9:
                    status_payload = printable[4:9]
                    status = parse_status_data(status_payload)
                    data = status
                    logger.info("Parsed status: %s", status)
                    data_event.set()
                else:
                    logger.info(
                        "Received data too short to parse status payload (len=%d)",
                        len(printable),
                    )
            except Exception:  # pragma: no cover - defensive
                logger.exception("Error handling notification")

        await self.client.start_notify(_TX_UUID, notification_handler)
        try:
            try:
                await asyncio.wait_for(data_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                # No data within timeout; return None
                pass
            return data
        finally:
            try:
                await self.client.stop_notify(_TX_UUID)
            except Exception:  # pragma: no cover - defensive cleanup
                logger.exception("Failed to stop notifications")
