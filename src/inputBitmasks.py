"""
inputBitmasks.py

Bitmasks / usage IDs for keyboard and mouse input for the CH9329,
which uses standard USB HID keyboard/mouse codes.

You import from here so you don't have to use magic numbers.
"""

# -----------------------
# Keyboard modifier bits
# (first byte of keyboard report)
# -----------------------
MOD_NONE       = 0x00
MOD_LCTRL      = 0x01  # bit 0
MOD_LSHIFT     = 0x02  # bit 1
MOD_LALT       = 0x04  # bit 2
MOD_LGUI       = 0x08  # bit 3 (Windows / Command key)
MOD_RCTRL      = 0x10  # bit 4
MOD_RSHIFT     = 0x20  # bit 5
MOD_RALT       = 0x40  # bit 6
MOD_RGUI       = 0x80  # bit 7

# -----------------------
# Mouse button bits
# (DATA[1] in the CH9329 relative mouse packet)
# -----------------------
MOUSE_LEFT     = 0x01  # bit 0
MOUSE_RIGHT    = 0x02  # bit 1
MOUSE_MIDDLE   = 0x04  # bit 2

# -----------------------
# Keyboard usage IDs (standard USB HID)
# Only a useful subset for now; extend as needed.
# -----------------------

# Letters
KEY_A = 0x04
KEY_B = 0x05
KEY_C = 0x06
KEY_D = 0x07
KEY_E = 0x08
KEY_F = 0x09
KEY_G = 0x0A
KEY_H = 0x0B
KEY_I = 0x0C
KEY_J = 0x0D
KEY_K = 0x0E
KEY_L = 0x0F
KEY_M = 0x10
KEY_N = 0x11
KEY_O = 0x12
KEY_P = 0x13
KEY_Q = 0x14
KEY_R = 0x15
KEY_S = 0x16
KEY_T = 0x17
KEY_U = 0x18
KEY_V = 0x19
KEY_W = 0x1A
KEY_X = 0x1B
KEY_Y = 0x1C
KEY_Z = 0x1D

# Number row (above letters)
KEY_1 = 0x1E
KEY_2 = 0x1F
KEY_3 = 0x20
KEY_4 = 0x21
KEY_5 = 0x22
KEY_6 = 0x23
KEY_7 = 0x24
KEY_8 = 0x25
KEY_9 = 0x26
KEY_0 = 0x27

# Common control keys
KEY_ENTER      = 0x28
KEY_ESCAPE     = 0x29
KEY_BACKSPACE  = 0x2A
KEY_TAB        = 0x2B
KEY_SPACE      = 0x2C

KEY_MINUS      = 0x2D  # -
KEY_EQUAL      = 0x2E  # =
KEY_LEFTBRACE  = 0x2F  # [
KEY_RIGHTBRACE = 0x30  # ]
KEY_BACKSLASH  = 0x31  # \
KEY_SEMICOLON  = 0x33  # ;
KEY_APOSTROPHE = 0x34  # '
KEY_GRAVE      = 0x35  # `
KEY_COMMA      = 0x36  # ,
KEY_DOT        = 0x37  # .
KEY_SLASH      = 0x38  # /

# Arrow keys
KEY_RIGHT      = 0x4F
KEY_LEFT       = 0x50
KEY_DOWN       = 0x51
KEY_UP         = 0x52

# Function keys
KEY_F1  = 0x3A
KEY_F2  = 0x3B
KEY_F3  = 0x3C
KEY_F4  = 0x3D
KEY_F5  = 0x3E
KEY_F6  = 0x3F
KEY_F7  = 0x40
KEY_F8  = 0x41
KEY_F9  = 0x42
KEY_F10 = 0x43
KEY_F11 = 0x44
KEY_F12 = 0x45
