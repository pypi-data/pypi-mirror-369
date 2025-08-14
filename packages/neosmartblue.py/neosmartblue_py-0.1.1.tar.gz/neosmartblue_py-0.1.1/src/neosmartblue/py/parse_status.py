def parse_status_data(status_data: bytes) -> dict:
    """
    Parse the 5-byte motor status payload.
    
    The status payload structure is:
      - Byte 0: Battery Level (0-100)
      - Byte 1: Target Position (%)
      - Byte 2: Limit Range Size (number of turns)
      - Byte 3: Current Position (%)
      - Byte 4: Flags (bit field)
    
    Flags:
      Bit 0 (0x01): Motor Running
      Bit 1 (0x02): Motor Direction (down if set)
      Bit 2 (0x04): Up Limit Set
      Bit 3 (0x08): Down Limit Set
      Bit 4 (0x10): Touch Control Active
      Bit 5 (0x20): Charging
      Bit 6 (0x40): Channel Setting Mode
      Bit 7 (0x80): Reverse Rotation
    
    Returns:
        dict: Parsed status values.
    """
    # Check if the status_data is exactly 5 bytes long
    # If not, raise a ValueError
    status_data_length = len(status_data)
    if status_data_length != 5:
        raise ValueError(f"Status data must be exactly 5 bytes long, but got {status_data_length} bytes.")
    
    battery_level = status_data[0]
    target_position = status_data[1]
    limit_range_size = status_data[2]
    current_position = status_data[3]
    flags = status_data[4]
    
    return {
        "battery_level": battery_level,
        "target_position": target_position,
        "limit_range_size": limit_range_size,
        "current_position": current_position,
        "motor_running": bool(flags & 0x01),
        "motor_direction_down": bool(flags & 0x02),
        "up_limit_set": bool(flags & 0x04),
        "down_limit_set": bool(flags & 0x08),
        "touch_control": bool(flags & 0x10),
        "charging": bool(flags & 0x20),
        "channel_setting_mode": bool(flags & 0x40),
        "reverse_rotation": bool(flags & 0x80),
    }
