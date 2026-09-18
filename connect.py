import serial
import pyautogui
import time
import math

# ============================================================
# Calliope Motion Mouse
# USB / Serial Version
# ============================================================

BAUD_RATE = 115200

BASE_SPEED_PPS = 900
DEADZONE = 45
CURVE = 1.20
FILTER = 0.15

SCROLL_DEADZONE = 80
SCROLL_SPEED = 8

INVERT_X = 1
INVERT_Y = 1

# ============================================================
# PyAutoGUI settings
# ============================================================

pyautogui.PAUSE = 0

print()
print("========================================")
print("        CALLIOPE MOTION MOUSE")
print("========================================")
print()

# ============================================================
# COM port
# ============================================================

port = input("Enter Calliope COM port (e.g. COM5): ").strip()

if not port:
    print("No COM port entered.")
    raise SystemExit

# ============================================================
# DPI
# ============================================================

print()
print("Mouse DPI")
print("Examples: 400 / 800 / 1200 / 1600 / 2400")
print()

dpi_input = input("Enter DPI: ").strip()

try:
    dpi = float(dpi_input)
except ValueError:
    print("Invalid DPI.")
    raise SystemExit

if dpi <= 0 or dpi > 10000:
    print("DPI must be between 1 and 10000.")
    raise SystemExit

DPI_MULTIPLIER = dpi / 800.0

# ============================================================
# Connection
# ============================================================

print()
print("Connecting to", port, "...")

try:
    ser = serial.Serial(
        port=port,
        baudrate=BAUD_RATE,
        timeout=0.05
    )

except serial.SerialException as e:
    print()
    print("Could not open the COM port.")
    print()
    print("Error:")
    print(e)
    raise SystemExit

print()
print("Calliope connected.")
print("Motion Mouse started.")
print()
print("A     = Left click")
print("B     = Right click")
print("A + B = Scroll")
print("Ctrl+C = Exit")
print()

# ============================================================
# Movement state
# ============================================================

filtered_x = 0.0
filtered_y = 0.0

remainder_x = 0.0
remainder_y = 0.0

last_time = time.perf_counter()

# ============================================================
# Deadzone
# ============================================================

def apply_deadzone(value, deadzone):

    if abs(value) <= deadzone:
        return 0.0

    if value > 0:
        return value - deadzone

    return value + deadzone


# ============================================================
# Movement curve
# ============================================================

def movement_curve(value):

    if value == 0:
        return 0.0

    sign = 1 if value > 0 else -1

    normalized = abs(value) / 1024.0

    if normalized > 1:
        normalized = 1

    curved = normalized ** CURVE

    return sign * curved


# ============================================================
# Main loop
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # Wait for incoming serial data
        # ----------------------------------------------------

        if ser.in_waiting <= 0:
            time.sleep(0.001)
            continue

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        # ----------------------------------------------------
        # Left click
        # ----------------------------------------------------

        if line == "CLICK_L":

            pyautogui.click(
                button="left",
                _pause=False
            )

            continue

        # ----------------------------------------------------
        # Right click
        # ----------------------------------------------------

        if line == "CLICK_R":

            pyautogui.click(
                button="right",
                _pause=False
            )

            continue

        # ----------------------------------------------------
        # Scroll
        # ----------------------------------------------------

        if line.startswith("SCROLL,"):

            try:

                value = float(
                    line.split(",", 1)[1]
                )

                if abs(value) > SCROLL_DEADZONE:

                    scroll_value = value / 1024.0
                    scroll_value *= SCROLL_SPEED
                    scroll_value *= DPI_MULTIPLIER

                    scroll_value = int(scroll_value)

                    if scroll_value != 0:

                        pyautogui.scroll(
                            -scroll_value,
                            _pause=False
                        )

            except (ValueError, IndexError):
                pass

            continue

        # ----------------------------------------------------
        # Mouse movement
        # ----------------------------------------------------

        if line.startswith("MOVE,"):

            try:

                parts = line.split(",")

                if len(parts) != 3:
                    continue

                raw_x = float(parts[1])
                raw_y = float(parts[2])

            except (ValueError, IndexError):
                continue

            # ------------------------------------------------
            # Apply deadzone
            # ------------------------------------------------

            raw_x = apply_deadzone(
                raw_x,
                DEADZONE
            )

            raw_y = apply_deadzone(
                raw_y,
                DEADZONE
            )

            # ------------------------------------------------
            # Smooth movement
            # ------------------------------------------------

            filtered_x = (
                filtered_x * (1.0 - FILTER)
                + raw_x * FILTER
            )

            filtered_y = (
                filtered_y * (1.0 - FILTER)
                + raw_y * FILTER
            )

            # ------------------------------------------------
            # Apply movement curve
            # ------------------------------------------------

            curved_x = movement_curve(
                filtered_x
            )

            curved_y = movement_curve(
                filtered_y
            )

            # ------------------------------------------------
            # Time-based movement
            # ------------------------------------------------

            now = time.perf_counter()

            dt = now - last_time
            last_time = now

            if dt > 0.05:
                dt = 0.05

            pixels_x = (
                curved_x
                * BASE_SPEED_PPS
                * dt
                * DPI_MULTIPLIER
                * INVERT_X
            )

            pixels_y = (
                curved_y
                * BASE_SPEED_PPS
                * dt
                * DPI_MULTIPLIER
                * INVERT_Y
            )

            # ------------------------------------------------
            # Preserve fractional pixels
            # ------------------------------------------------

            remainder_x += pixels_x
            remainder_y += pixels_y

            move_x = math.trunc(
                remainder_x
            )

            move_y = math.trunc(
                remainder_y
            )

            remainder_x -= move_x
            remainder_y -= move_y

            # ------------------------------------------------
            # Move cursor
            # ------------------------------------------------

            if move_x != 0 or move_y != 0:

                pyautogui.moveRel(
                    move_x,
                    move_y,
                    duration=0,
                    _pause=False
                )


# ============================================================
# Exit handling
# ============================================================

except pyautogui.FailSafeException:

    print()
    print("PyAutoGUI failsafe triggered.")
    print("The cursor reached a screen corner.")

except KeyboardInterrupt:

    print()
    print("Motion Mouse stopped.")

finally:

    try:
        ser.close()
    except Exception:
        pass

    print()
    print("Serial connection closed.")