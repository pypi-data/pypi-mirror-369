# NeoSmartBlue Python Library

A Python library for controlling Neo Smart Blinds via BlueLink Bluetooth connection.

## Installation

```bash
pip install neosmartblue.py
```

## Usage

### Scanning for devices and reading status from advertisements

```python
import asyncio
from neosmartblue.py import scan_for_devices

async def main():
    # Scan for nearby Neo Smart Blinds devices
    devices = await scan_for_devices(timeout=15.0)
    if not devices:
        print("No devices found.")
        return
    
    for device in devices:
        print(f"Device Address: {device['address']}")
        print(f"Device Name: {device['name']}")
        print("Status:")
        for key, value in device['status'].items():
            print(f"  {key}: {value}")
        print()


asyncio.run(main())
```

### Controlling a device

```python
import asyncio
from neosmartblue.py import BlueLinkDevice

async def main():
    # Replace with your device's MAC address
    device = BlueLinkDevice("XX:XX:XX:XX:XX:XX")
    
    # Connect to the device
    await device.connect()
    
    try:
        # Move blinds to 50% closed position
        await device.move_to_position(50)
        
        # Stop movement if needed
        # await device.stop()
    
    finally:
        # Disconnect from device
        await device.disconnect()

asyncio.run(main())
```