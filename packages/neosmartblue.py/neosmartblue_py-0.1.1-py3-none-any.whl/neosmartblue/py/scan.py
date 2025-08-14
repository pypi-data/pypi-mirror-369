from typing import Dict, List, Any
from bleak import BleakScanner

from .parse_status import parse_status_data

async def scan_for_devices(timeout: float = 15.0) -> List[Dict[str, Any]]:
    """
    Scan for Neo Smart Blinds devices and return their advertisement data.
    
    Parameters:
        timeout (float): The number of seconds to scan for devices.
        
    Returns:
        List[Dict[str, Any]]: List of discovered devices with their status information.
    """
    devices = []
    
    def detection_callback(device, advertisement_data):
        device_address = device.address  # Define device_address
        
        if device.name and (device.name.startswith("NEO-") or device.name.startswith("NMB-")):
            if advertisement_data.manufacturer_data:
                manufacturer_data = advertisement_data.manufacturer_data  # Extract manufacturer data   
                byte_data = manufacturer_data[2407]  # Get the first manufacturer data entry
                # Convert to bytearray
                status_payload = bytearray(byte_data)
                if status_payload:
                    status = parse_status_data(status_payload)
                    devices.append({
                            "address": device_address,
                            "name": device.name,
                            "status": status
                        })
            else:
                # If no status data is found, still add the device with empty status
                devices.append({
                        "address": device_address,
                        "name": device.name,
                        "status": {}
                        })
   
        # We don't need to return anything as we're already adding to devices list
        
    scanner = await BleakScanner.discover(return_adv=True, timeout=timeout)
    for device_address, (ble_device, adv_data) in scanner.items():
        detection_callback(ble_device, adv_data)
    
    return devices