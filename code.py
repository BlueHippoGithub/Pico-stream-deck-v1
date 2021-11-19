import adafruit_ssd1306, board, busio, displayio, digitalio, usb_hid
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl
from keyboard_layout_win_da import KeyboardLayout
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

        sleep(0.75)
        self.layout.write("ssh blue@IPADDRESS\n")

        sleep(0.75)
        self.layout.write("SERVERPASSWORD\n")

    def auto_update(self):
        self.layout.write("sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y\n")
    
    def restart_server(self):
        self.layout.write("sudo reboot\n")

    def playpause(self):
        self.consumer_control.send(0xCD)

    def mute(self):
        self.consumer_control.send(0xE2)

    def skip(self):
        self.consumer_control.send(0xB5)

    def default_password(self):
        self.layout.write("DEFAULTPASSWORD\n")

    def complex_password(self):
        self.layout.write("COMPLEXPASSWORD\n")
    
    def old_password(self):
        self.layout.write("OLDPASSWORD\n")

    #Open spotify using win + r to open run
    def spotify(self):
        self.keyboard.press(Keycode.WINDOWS, Keycode.R)
        self.keyboard.release(Keycode.WINDOWS, Keycode.R)
        sleep(0.1)
        self.layout.write("spotify\n")

    def discord(self):
        self.keyboard.press(Keycode.WINDOWS, Keycode.R)
        self.keyboard.release(Keycode.WINDOWS, Keycode.R)
        sleep(0.1)
        self.layout.write(r"C:\Users\Blue\AppData\Local\Discord\Update.exe --processStart Discord.exe")
        self.keyboard.press(Keycode.RETURN)
        self.keyboard.release(Keycode.RETURN)

    def steam(self):
        self.keyboard.press(Keycode.WINDOWS, Keycode.R)
        self.keyboard.release(Keycode.WINDOWS, Keycode.R)
        sleep(0.1)
        self.layout.write("C:\Program Files (x86)\Steam\Steam.exe\n")


#Layout class to handle different layouts
#inherits macrofunctions to map functions to each screen/button
class Layouts(MacroFunctions):
    def __init__(self, display, keyboard, layout, consumer_control):
        super().__init__(display, keyboard, layout, consumer_control)
        self.display = display
        self.keyboard = keyboard
        self.layout = layout
        self.consumer_control = consumer_control

        self.functions = []
        self.home()
        self.mainloop()

    #Default start screen
    def home(self):
        self.functions = [self.server, self.passwords, self.mediaControls, self.programs]
        self.display.display_text(1, "Server")
        self.display.display_text(2, "Passwords")
        self.display.display_text(3, "Media Controls")
        self.display.display_text(4, "Programs")
        
    def server(self):
        self.functions = [self.home, self.auto_ssh, self.auto_update, self.restart_server]
        self.display.display_text(1, "Home Screen")
        self.display.display_text(2, "Auto SSH")
        self.display.display_text(3, "Auto update")
        self.display.display_text(4, "Restart now")

    def mediaControls(self):
        self.functions = [self.home, self.mute, self.playpause, self.skip]
        self.display.display_text(1, "Home Screen")
        self.display.display_text(2, "Mute/Unmute")
        self.display.display_text(3, "Play/Pause")
        self.display.display_text(4, "Skip")
    
    def programs(self):
        self.functions = [self.home, self.spotify, self.discord, self.steam]
        self.display.display_text(1, "Home Screen")
        self.display.display_text(2, "Spotify")
        self.display.display_text(3, "Discord")
        self.display.display_text(4, "Steam")

    def passwords(self):
        self.functions = [self.home, self.default_password, self.complex_password, self.old_password]
        self.display.display_text(1, "Home Screen")
        self.display.display_text(2, "Default Password")
        self.display.display_text(3, "Complex Password")
        self.display.display_text(4, "Old Password")

    #Main loop to check if buttons have been pressed
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

#Start everything up
def main():
    keyboard=Keyboard(usb_hid.devices)
    layout = KeyboardLayout(keyboard)
    consumer_control = ConsumerControl(usb_hid.devices)

    display = Display(scl=board.GP1, sda=board.GP0, 
        s0=board.GP20, s1=board.GP19, s2=board.GP10)

    layouts = Layouts(display, keyboard, layout, consumer_control)
    layouts.mainloop()


if __name__ == "__main__":
    main()
    
