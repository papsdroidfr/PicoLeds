# runs on PICO

import array, time, rp2
from machine import Pin

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

class LedsRGBws2812:
    ''' Neopixel RGB WS2812 Class
        instance: leds = LedsRGBws2812() or LedsRGBws2812(n_leds, pin_num, brightness)
    '''

    def __init__(self, n_leds=16, pin_num=6, brightness=0.2):
        ''' constructor: Configure the WS2812 LEDs. '''
        
        print('init leds RGB')
        self.NUM_LEDS = n_leds
        self.PIN_NUM = pin_num
        self.brightness = brightness
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 150, 0)
        self.GREEN = (0, 255, 0)
        self.CYAN = (0, 255, 255)
        self.BLUE = (0, 0, 255)
        self.PURPLE = (180, 0, 255)
        self.WHITE = (255, 255, 255)
        self.MORNING = (65,63,20)
        self.COLORS = (self.MORNING, self.WHITE, self.PURPLE, self.BLUE)

    
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(self.PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])


    def pixels_show(self):
        ''' add data into sm FIFO: show de pixels '''
        dimmer_ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness)
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
        time.sleep_ms(10)

    def pixels_set(self, i, color):
        ''' set pixel number i with color=(r,g,b) '''
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

    def pixels_fill(self, color):
        ''' set all pixels with same color (r,g,b) '''
        for i in range(len(self.ar)):
            self.pixels_set(i, color)

    def pixels_off(self):
        self.pixels_fill(self.BLACK)
        self.pixels_show()
        
    def color_chase(self, color, wait):
        ''' color(r,g,b) grow from pixel 0 to the end.'''
        for i in range(self.NUM_LEDS):
            self.pixels_set(i, color)
            time.sleep(wait)
            self.pixels_show()
        time.sleep(0.2)
 
    def wheel(self, pos):
        ''' Input a value 0 to 255 to get a color value (r,g,b).
            The colours are a transition r - g - b - back to r.
        '''
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)
 
 
    def rainbow_cycle(self, wait=0):
        ''' move colors in a rainbow cycle '''
        for j in range(255):
            for i in range(self.NUM_LEDS):
                rc_index = (i * 256 // self.NUM_LEDS) + j
                self.pixels_set(i, self.wheel(rc_index & 255))
            self.pixels_show()
            time.sleep(wait)
    
    def fade_out(self, n_steps, color, wait):
        ''' fade out color(r,g,b) to BLACK in n_steps   '''
        r_delta, g_delta, b_delta = color[0]//n_steps, color[1]//n_steps, color[2]//n_steps
        for j in range(n_steps):
            self.pixels_fill( (color[0]-j*r_delta , color[1]-j*g_delta , color[2]-j*b_delta) )
            self.pixels_show()
            time.sleep(wait)
        self.pixels_off()
        time.sleep(wait)

    def fade_in(self, n_steps, color, wait):
        ''' fade in from BLACK to color(r,g,b) in n_steps   '''
        r_delta, g_delta, b_delta = color[0]//n_steps, color[1]//n_steps, color[2]//n_steps
        for j in range(n_steps, 0, -1 ):
            self.pixels_fill( (color[0]-j*r_delta , color[1]-j*g_delta , color[2]-j*b_delta) )
            self.pixels_show()
            time.sleep(wait)
        time.sleep(wait)


class Application:
    
    def __init__(self):
        ''' initialize leds RGB and push Button'''
        self.leds = LedsRGBws2812(brightness=1)
        self.button = Pin(7, Pin.IN, Pin.PULL_UP)
        #self.leds.rainbow_cycle()
        self.id_color=0
        self.leds.fade_in(10, self.leds.COLORS[0], 0.05)
        #callback function called with push button
        self.button.irq(self.callback, Pin.IRQ_FALLING)
        self.loop()  #inifinite loop of events 
        
    
    def callback(self, pin):
        ''' callback function called when buton is pushed '''
        time.sleep(0.05) # wait 50ms : stabilization to avoid rebounds.
        if not(self.button.value()): # buton still pressed after the stabilization period ?
            #print('button pressed', pin.irq().flags())
            self.leds.fade_out(10, self.leds.COLORS[self.id_color], 0.05)
            self.id_color = (self.id_color+1) % (len(self.leds.COLORS)) 
            #self.leds.color_chase(self.leds.COLORS[self.id_color], 0.05)
            self.leds.fade_in(10, self.leds.COLORS[self.id_color], 0.05)
            
    
    def loop(self):
        while(True):
            time.sleep(0.2)


appl=Application()


