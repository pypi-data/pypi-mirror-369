
def generate_move_command(position: int) -> bytes:
    """
    Generate a command to move the blinds to a specified position.
    
    Parameters:
        position (int): A value between 0 (fully open) and 100 (fully closed).
        
    Returns:
        bytes: The complete BLE command.
    
    Example:
        For a 50% position, the command is:
        9A 00 00 00 DD 32 EF
        (0x32 is 50 in decimal and EF is the parity byte: 0xDD XOR 0x32)
    """
    if not (0 <= position <= 100):
        raise ValueError("Position must be between 0 (fully open) and 100 (fully closed)")
    header = bytes([0x00, 0x00, 0x00, 0xDD])
    parity = 0xDD ^ position  # Calculate parity byte
    return bytes([0x9A]) + header + bytes([position, parity])


def generate_stop_command() -> bytes:
    """
    Generate a command to immediately stop motor movement.
    
    The fixed payload is:
        9A 00 00 00 0A CC C6
    """
    return bytes([0x9A, 0x00, 0x00, 0x00, 0x0A, 0xCC, 0xC6])


def generate_status_update_command() -> bytes:
    """
    Generate a command to request a status update from the device.
    
    The fixed payload is:
        9A 00 00 00 CC CC 00
    """
    return bytes([0x9A, 0x00, 0x00, 0x00, 0xCC, 0xCC, 0x00])


def generate_jog_command() -> bytes:
    """
    Generate a command to initiate a jog (short up/down movement).
    
    The command code is 0x85.
    """
    return bytes([0x85])


def generate_ping_command() -> bytes:
    """
    Generate a keep-alive ping command to maintain the BLE connection.
    
    The command code is 0x80.
    """
    return bytes([0x80])
