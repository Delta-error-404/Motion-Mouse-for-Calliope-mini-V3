# Motion-Mouse-for-Calliope-mini-V3
A Calliope mini V3 program for controlling your computer mouse using motion and buttons. (Build with AI)

# Calliope Motion Mouse

A USB-powered motion-controlled mouse using a **Calliope mini V3** and a Windows PC.

Move the Calliope mini to control the mouse cursor, use the buttons for clicking, and hold both buttons to scroll.

No Bluetooth required. Everything works through a USB serial connection.

---

## Features

- Motion-controlled mouse cursor
- Calliope mini V3 accelerometer support
- USB serial communication
- Left click with Button A
- Right click with Button B
- Scroll mode with A + B
- Adjustable DPI
- Configurable movement speed
- Deadzone to reduce sensor drift
- Movement smoothing
- Non-linear movement curve
- Fractional-pixel movement handling
- PyAutoGUI failsafe remains enabled
- Can be compiled into a standalone Windows `.exe`
- No accounts or cloud services required
- No Bluetooth required

---

## How it works

The Calliope mini V3 reads its accelerometer and button states.

It sends simple commands over USB serial:

```text
MOVE,x,y
CLICK_L
CLICK_R
SCROLL,y
