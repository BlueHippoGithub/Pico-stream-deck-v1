<h1>Pico Stream Deck / Macro Keyboard v1</h1>

This is v1 of my streamdeck on a pico.
So far it's very basic and uses circuitpython to emulate a USB HID device, it does so very well but the screens imo update a bit too slow.

Parts list:
  - ssd1306 OLED screen (128x32)
  - 74HC4051 8 channel analog multiplexer
  - Raspberry Pi Pico
  - Buttons
  - Prototype PCB


Required libraries/files:
  - adafruit_bus_device
  - adafruit_display_text
  - adafruit_hid
  - adafruit_framebuf.py
  - adafruit_ssd1306.py
  - font5x8.bin
