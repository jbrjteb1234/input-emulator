"""
inputEvent.py

Helper functions for talking to a CH9329 over a CP2102 serial link.

Requires:
    pip install pyserial

And your wiring:
    CP2102 TXD -> CH9329 RX
    CP2102 RXD -> CH9329 TX
    CP2102 GND -> CH9329 GND
(5V is NOT connected between boards; each board is powered by its own USB.)

The CH9329 is assumed to be in protocol mode at 9600 8N1.
"""

import time
import serial

from inputBitmasks import (
    MOD_NONE,
    MOUSE_LEFT,
    MOUSE_RIGHT,
    MOUSE_MIDDLE,
)

# ---------- Protocol constants (from CH9329 docs) ----------

HEAD = [0x57, 0xAB]
ADDR_DEFAULT = 0x00

CMD_SEND_KB_GENERAL_DATA = 0x02  # keyboard report
CMD_SEND_MS_REL_DATA     = 0x05  # relative mouse move/click

# New: configuration / reset commands
CMD_GET_PARA_CFG         = 0x08
CMD_SET_PARA_CFG         = 0x09
CMD_RESET                = 0x0F



# ---------- Serial helper ----------

def open_serial(port: str, baudrate: int = 9600, timeout: float = 0.2) -> serial.Serial:
    """
    Open the CP2102 serial port connected to the CH9329.

    :param port: e.g. "COM3" on Windows or "/dev/ttyUSB0" on Linux.
    """
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
        write_timeout=1.0,
    )
    return ser


# ---------- Internal helpers ----------

def _checksum(parts: list[int]) -> int:
    """Return low 8 bits of the sum of all bytes in `parts`."""
    return sum(parts) & 0xFF

def _build_frame(cmd: int, data: list[int], addr: int = ADDR_DEFAULT) -> bytes:
    """
    Build a generic CH9329 command frame.

    Format: HEAD(2) + ADDR(1) + CMD(1) + LEN(1) + DATA(N) + SUM(1)
    """
    length = len(data) & 0xFF
    frame_wo_sum = HEAD + [addr & 0xFF, cmd & 0xFF, length] + [b & 0xFF for b in data]
    checksum = _checksum(frame_wo_sum)
    return bytes(frame_wo_sum + [checksum & 0xFF])

def _get_parameter_block(ser: serial.Serial) -> list[int]:
    """
    Read the 50-byte parameter configuration block from the CH9329
    using CMD_GET_PARA_CFG (0x08).

    Returns a list of 50 ints.
    """
    # Clear any old responses
    ser.reset_input_buffer()

    # Send: HEAD, ADDR, 0x08, LEN=0, SUM
    frame = _build_frame(CMD_GET_PARA_CFG, [])
    ser.write(frame)
    ser.flush()

    expected_len = 2 + 1 + 1 + 1 + 50 + 1  # HEAD(2)+ADDR+CMD+LEN+DATA(50)+SUM
    resp = ser.read(expected_len)

    if len(resp) != expected_len:
        raise RuntimeError(f"Timeout or short read from CH9329 (got {len(resp)} bytes, expected {expected_len})")

    # Basic sanity checks
    if resp[0] != HEAD[0] or resp[1] != HEAD[1]:
        raise RuntimeError("Bad frame header in CMD_GET_PARA_CFG response")

    if resp[3] != (CMD_GET_PARA_CFG | 0x80):  # normal response CMD = 0x08 | 0x80 = 0x88
        raise RuntimeError(f"Unexpected CMD in CMD_GET_PARA_CFG response: 0x{resp[3]:02X}")

    if resp[4] != 50:
        raise RuntimeError(f"Unexpected parameter length in response: {resp[4]} (expected 50)")

    data = list(resp[5:5+50])

    # (Optional) checksum check:
    calc_sum = _checksum(list(resp[:-1]))
    if (calc_sum & 0xFF) != resp[-1]:
        raise RuntimeError("Checksum mismatch in CMD_GET_PARA_CFG response")

    return data


def _set_parameter_block(ser: serial.Serial, params: list[int]) -> None:
    """
    Write a 50-byte parameter configuration block to the CH9329
    using CMD_SET_PARA_CFG (0x09).

    `params` must be a list of exactly 50 ints.
    """
    if len(params) != 50:
        raise ValueError("Parameter block must be exactly 50 bytes")

    ser.reset_input_buffer()

    frame = _build_frame(CMD_SET_PARA_CFG, [b & 0xFF for b in params])
    ser.write(frame)
    ser.flush()

    # Response: HEAD, ADDR, 0x89, LEN=1, STATUS, SUM  (total 7 bytes)
    expected_len = 2 + 1 + 1 + 1 + 1 + 1
    resp = ser.read(expected_len)

    if len(resp) != expected_len:
        raise RuntimeError("Timeout waiting for CMD_SET_PARA_CFG response")

    if resp[0] != HEAD[0] or resp[1] != HEAD[1]:
        raise RuntimeError("Bad frame header in CMD_SET_PARA_CFG response")

    if resp[3] != (CMD_SET_PARA_CFG | 0x80):  # 0x09 | 0x80 = 0x89
        raise RuntimeError(f"Unexpected CMD in CMD_SET_PARA_CFG response: 0x{resp[3]:02X}")

    status = resp[5]
    if status != 0x00:
        raise RuntimeError(f"CH9329 reported error status 0x{status:02X} to CMD_SET_PARA_CFG")

    # (Optional) checksum check:
    calc_sum = _checksum(list(resp[:-1]))
    if (calc_sum & 0xFF) != resp[-1]:
        raise RuntimeError("Checksum mismatch in CMD_SET_PARA_CFG response")
    
# ---------- Config helpers ----------

def set_baudrate_115200(ser: serial.Serial) -> None:
    """
    Permanently change the CH9329's UART baudrate setting to 115200 bps.

    Call this while the chip is still at its current baud (normally 9600).
    The new baudrate is stored in the chip's NVM and becomes active on the
    **next power-on or reset**.

    NOTE: 115200 is only supported when the CH9329 is powered from 5V.
    """

    # 1) Fetch current parameter block
    params = _get_parameter_block(ser)

    # 2) Overwrite the 4-byte baud field (index 3..6, big-endian)
    baud_bytes = (115200).to_bytes(4, "big")  # 0x00 0x01 0xC2 0x00
    params[3:7] = list(baud_bytes)

    # 3) Write it back
    _set_parameter_block(ser, params)

    # At this point the new baud is stored, but **still running at old baud**
    # until next power-cycle or CMD_RESET + reopen at 115200.


# ---------- Keyboard helpers ----------

def _build_keyboard_frame(
    keycodes: list[int],
    modifiers: int = MOD_NONE,
    addr: int = ADDR_DEFAULT,
) -> bytes:
    """
    Build a CMD_SEND_KB_GENERAL_DATA frame.

    Data format (8 bytes) is the standard HID boot keyboard report:
      DATA[0] = modifier bits (Ctrl/Shift/Alt/GUI)
      DATA[1] = reserved (0)
      DATA[2..7] = up to 6 key usage codes, 0 meaning "no key".
    """

    # Ensure at most 6 keys
    keycodes = list(keycodes[:6])
    # Pad with zeros to length 6
    while len(keycodes) < 6:
        keycodes.append(0x00)

    data = [
        modifiers & 0xFF,  # DATA[0]
        0x00,              # DATA[1] reserved
        *keycodes,         # DATA[2]..[7]
    ]

    cmd = CMD_SEND_KB_GENERAL_DATA
    length = len(data)  # always 8

    frame_wo_sum = HEAD + [addr, cmd, length] + data
    checksum = _checksum(frame_wo_sum)
    return bytes(frame_wo_sum + [checksum])


def send_keyboard_report(
    ser: serial.Serial,
    keycodes: list[int],
    modifiers: int = MOD_NONE,
):
    """
    Send a raw keyboard report (combination keys).

    :param keycodes: list of usage IDs (max 6), e.g. [KEY_A] or [KEY_A, KEY_B]
    :param modifiers: modifier mask, e.g. MOD_LSHIFT | MOD_LCTRL
    """
    frame = _build_keyboard_frame(keycodes, modifiers)
    ser.write(frame)
    ser.flush()


def key_down(
    ser: serial.Serial,
    keycode: int,
    modifiers: int = MOD_NONE,
):
    """
    Press a key (or a key with modifiers).

    Example:
        key_down(ser, KEY_A)                 # 'a'
        key_down(ser, KEY_A, MOD_LSHIFT)     # 'A'
    """
    send_keyboard_report(ser, [keycode], modifiers)


def key_up(ser: serial.Serial):
    """
    Release all keys (clears modifiers and keycodes).

    For simple use where you press one key at a time, this is enough.
    """
    send_keyboard_report(ser, [], MOD_NONE)


def key_tap(
    ser: serial.Serial,
    keycode: int,
    modifiers: int = MOD_NONE,
    delay: float = 0.03,
):
    import random

    
    travel_delay = random.uniform(0.05, 0.4)

   
    jitter_factor = random.uniform(0.6, 1.4)
    dwell_delay = max(0.02, delay * jitter_factor)

    time.sleep(travel_delay)

    key_down(ser, keycode, modifiers)

    time.sleep(dwell_delay)

    key_up(ser)



# ---------- Mouse helpers ----------

def _encode_relative_delta(delta: int) -> int:
    """
    Encode a signed delta into CH9329 relative format:

      0x00   = no movement
      0x01–0x7F = +1..+127 pixels
      0x80–0xFF = negative, pixels = 256 - value
    """
    if delta == 0:
        return 0x00

    if delta > 127:
        delta = 127
    if delta < -127:
        delta = -127

    if delta > 0:
        return delta & 0xFF
    else:
        return (0x100 - (-delta)) & 0xFF


def _build_mouse_rel_frame(
    dx: int,
    dy: int,
    buttons: int = 0x00,
    wheel: int = 0x00,
    addr: int = ADDR_DEFAULT,
) -> bytes:
    """
    Build a CMD_SEND_MS_REL_DATA frame (relative mouse movement/click).

    Data[0] = 0x01 (must be 0x01)
    Data[1] = button bits (bit0=left, bit1=right, bit2=middle)
    Data[2] = X delta (encoded)
    Data[3] = Y delta (encoded)
    Data[4] = wheel delta (0 = none)
    """
    x_byte = _encode_relative_delta(dx)
    y_byte = _encode_relative_delta(dy)

    data = [
        0x01,
        buttons & (MOUSE_LEFT | MOUSE_RIGHT | MOUSE_MIDDLE),
        x_byte,
        y_byte,
        wheel & 0xFF,
    ]

    cmd = CMD_SEND_MS_REL_DATA
    length = len(data)

    frame_wo_sum = HEAD + [addr, cmd, length] + data
    checksum = _checksum(frame_wo_sum)
    return bytes(frame_wo_sum + [checksum])


def mouse_move(
    ser: serial.Serial,
    dx: int,
    dy: int,
    buttons: int = 0x00,
    wheel: int = 0x00,
):
    """
    Move the mouse by (dx, dy) with optional buttons held and wheel scroll.

    To just move:
        mouse_move(ser, 50, 0)

    To move while left button is held (drag):
        mouse_move(ser, 10, 0, buttons=MOUSE_LEFT)
    """
    frame = _build_mouse_rel_frame(dx, dy, buttons, wheel)
    ser.write(frame)
    ser.flush()


def mouse_down(ser: serial.Serial, button_mask: int):
    """
    Press one or more mouse buttons without moving.

    Example:
        mouse_down(ser, MOUSE_LEFT)
        mouse_down(ser, MOUSE_LEFT | MOUSE_RIGHT)
    """
    frame = _build_mouse_rel_frame(0, 0, buttons=button_mask)
    ser.write(frame)
    ser.flush()


def mouse_up(ser: serial.Serial):
    """
    Release all mouse buttons (no movement).
    """
    frame = _build_mouse_rel_frame(0, 0, buttons=0x00)
    ser.write(frame)
    ser.flush()
