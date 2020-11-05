# clock_batt.py Battery powered clock demo for Pyboard/Adafruit sharp 2.7" display

# Copyright (c) 2020 Peter Hinch
# Released under the MIT license. See LICENSE

# HARDWARE
# This assumes a Pybaord D in WBUS-DIP28 and powered by a LiPo cell
# WIRING
# Pyb   SSD
# Vin   Vin  Pyboard D: Vin on DIP28 is an output when powered by LiPo
# Gnd   Gnd
# Y8    DI
# Y6    CLK
# Y5    CS


# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

import machine
import gc
from drivers.sharp.sharp import SHARP as SSD

# Initialise hardware
pcs = machine.Pin('Y5', machine.Pin.OUT_PP, value=0)  # Active high
spi = machine.SPI(2)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs)

# Now import other modules
import upower
from gui.core.nanogui import refresh
from gui.widgets.label import Label
from gui.widgets.dial import Dial, Pointer

import pyb
import cmath

from gui.core.writer import Writer

# Fonts for Writer
import gui.fonts.freesans20 as font_small
import gui.fonts.arial35 as font_large

refresh(ssd)  # Initialise display.

def aclock():
    rtc = pyb.RTC()
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    days = ('Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun')
    months = ('Jan', 'Feb', 'March', 'April', 'May', 'June', 'July',
              'Aug', 'Sept', 'Oct', 'Nov', 'Dec')
    # Instantiate Writer
    Writer.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
    wri = Writer(ssd, font_small, verbose=False)
    wri.set_clip(True, True, False)
    wri_tim = Writer(ssd, font_large, verbose=False)
    wri_tim.set_clip(True, True, False)

    # Instantiate displayable objects
    dial = Dial(wri, 2, 2, height = 215, ticks = 12, bdcolor=None, pip=True)
    lbltim = Label(wri_tim, 50, 230, '00.00.00')
    lbldat = Label(wri, 100, 230, 100)
    hrs = Pointer(dial)
    mins = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.92j
    while True:
        t = rtc.datetime()  # (year, month, day, weekday, hours, minutes, seconds, subseconds)
        hang = -t[4]*pi/6 - t[5]*pi/360  # Angles of hands in radians
        mang = -t[5] * pi/30
        if abs(hang - mang) < pi/360:  # Avoid visually confusing overlap of hands
            hang += pi/30  # by making hr hand lag slightly
        hrs.value(hstart * uv(hang))
        mins.value(mstart * uv(mang))
        lbltim.value('{:02d}.{:02d}'.format(t[4], t[5]))
        lbldat.value('{} {} {} {}'.format(days[t[3] - 1], t[2], months[t[1] - 1], t[0]))
        refresh(ssd)
        # Power saving: only refresh every 30s
        for _ in range(30):
            upower.lpdelay(1000)
            ssd.update()  # Toggle VCOM

aclock()
