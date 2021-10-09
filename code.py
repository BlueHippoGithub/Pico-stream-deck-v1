import adafruit_ssd1306, board, busio, displayio, digitalio, usb_hid
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from time import sleep

class Display:
    def __init__(self, scl, sda, s0, s1, s2):
        self.s0 = digitalio.DigitalInOut(s0)
        self.s0.direction = digitalio.Direction.OUTPUT

        self.s1 = digitalio.DigitalInOut(s1)
        self.s1.direction = digitalio.Direction.OUTPUT

        #4 screens means I only need to use 2 set pins
        #self.s2 = digitalio.DigitalInOut(s2)
        #self.s2.direction = digitalio.Direction.OUTPUT

        self.i2c = busio.I2C(scl=scl, sda=sda)

        self.display = None

        #Replace with the truth table that fits your multiplexer
        #I tested this with 6 screens, hence the 6 items in the array
        self.truth_table = [
            [False, False, False],
            [True, False, False],
            [False, True, False],
            [True, True, False],
            [False, False, True],
            [True, False, True]]
        
        #4 Because I have 4 screens connected
        #This initializes the screens so they're blank and ready to receive data
        for i in range(4):
            self.set_pins(self.truth_table[i])
            self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, self.i2c)

    def set_pins(self, truth_array):
        self.s0.value = truth_array[0]
        self.s1.value = truth_array[1]
        #self.s2.value = truth_array[2]

    def display_text(self, screen, text, invert = False):
        screen_num = screen - 1

        #Center text on screen
        location_x = (128/2) - (len(text) *3)
        self.set_pins(self.truth_table[screen_num])
        self.display.fill(1 if invert else 0)
        self.display.text(text, int(location_x), 12, not invert)
        self.display.show()

class MacroFunctions():
    def __init__(self, display, keyboard, layout, consumer_control):
        self.display = display
        self.keyboard = keyboard
        self.layout = layout
        self.consumer_control = consumer_control

        #Create array of buttons matching the screens
        self.buttons = [digitalio.DigitalInOut(board.GP8),digitalio.DigitalInOut(board.GP14),
        digitalio.DigitalInOut(board.GP15),digitalio.DigitalInOut(board.GP9)]
    
        for i in self.buttons:
            i.switch_to_input(pull=digitalio.Pull.DOWN)


    def auto_ssh(self):
        self.keyboard.press(Keycode.WINDOWS, Keycode.R)
        self.keyboard.release(Keycode.WINDOWS, Keycode.R)
        
        sleep(0.05)
        self.layout.write("cmd\n")

        sleep(1)
        self.layout.write("ssh blue")

        #I have a danish keyboard and this creates the @ sign on my PC, may vary for your layout
        self.keyboard.press(Keycode.CONTROL, Keycode.ALT, Keycode.TWO)
        self.keyboard.release(Keycode.CONTROL, Keycode.ALT, Keycode.TWO)

        self.layout.write("192.168.1.114\n")

        sleep(0.75)
        self.layout.write("PASSWORD\n")

    #Consumer control uses the hexadecimals from the official USB HID documentation
    def playpause(self):
        self.consumer_control.press(0xCD)
        sleep(0.05)
        self.consumer_control.release()

    def mute(self):
        self.consumer_control.press(0xE2)
        sleep(0.05)
        self.consumer_control.release()
    
    def default_password(self):
        self.layout.write("DEFAULTPASS")
        sleep(0.01)
        self.keyboard.send(Keycode.RETURN)
    
    def complex_password(self):
        self.layout.write("COMPLEXPASS")
        sleep(0.01)
        self.keyboard.send(Keycode.RETURN)
    
    def old_password(self):
        self.layout.write("OLDPASS")
        sleep(0.01)
        self.keyboard.send(Keycode.RETURN)

    #Open spotify using win + r to open run
    def spotify(self):
        self.keyboard.press(Keycode.WINDOWS, Keycode.R)
        self.keyboard.release(Keycode.WINDOWS, Keycode.R)
        sleep(0.05)
        self.layout.write("spotify\n")

class Layouts(MacroFunctions):
    def __init__(self, display, keyboard, layout, consumer_control):
        super().__init__(display, keyboard, layout, consumer_control)
        self.display = display
        self.keyboard = keyboard
        self.layout = layout
        self.consumer_control = consumer_control

        self.functions = []
        self.home()

    def home(self):
        self.functions = [self.auto_ssh, self.passwords, self.mute, self.spotify]
        self.display.display_text(1, "Auto SSH")
        self.display.display_text(2, "Passwords")
        self.display.display_text(3, "Mute PC")
        self.display.display_text(4, "Spotify")
        
        self.mainloop()
    
    def passwords(self):
        self.functions = [self.home, self.default_password, self.complex_password, self.old_password]
        self.display.display_text(1, "Home Screen")
        self.display.display_text(2, "Default Password")
        self.display.display_text(3, "Complex Password")
        self.display.display_text(4, "Old Password")

        self.mainloop()

    def mainloop(self):
        while True:
            y = 0
            for i in self.buttons:
                if(i.value == True):
                    self.functions[y]()
                    while(i.value == True):
                        pass
                y += 1

            sleep(0.05)

def main():
    keyboard=Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(keyboard)
    consumer_control = ConsumerControl(usb_hid.devices)

    display = Display(scl=board.GP1, sda=board.GP0, 
        s0=board.GP20, s1=board.GP19, s2=board.GP10)

    layouts = Layouts(display, keyboard, layout, consumer_control)
    layouts.mainloop()


if __name__ == "__main__":
    main()
