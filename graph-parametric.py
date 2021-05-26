#!/usr/local/bin/python3

import sys
import functools as ft
import itertools as it
import math
import turtle as t
import re
from time import sleep
import expr

mag_by = 1

class CurveSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.expr_set = expr.ExprSet(file_name=file_name)
        self.total_points = self.expr_set.eval_for("points", missing=1000)
        self.wave_speed = self.expr_set.eval_for("wave_speed", missing=0.0)
        self.linear_speed = self.expr_set.eval_for("linear_speed", missing=0.0)
        self.color_spin = self.expr_set.eval_for("color_speed")
        self.line_width = self.expr_set.eval_for("line_width", missing=1)
        self.screen_size = self.expr_set.eval_for("screen_size", missing=1.0)
        self.points = self.expr_set.eval_for("points", missing=1000)

        self.color_change_steps = int(self.total_points / 200)
        if self.color_change_steps == 0:
            self.color_change_steps = 1

    def draw_frame(self, wave_point, linear_point):
        global mag_by

        t.up()
        first = True
        t.width(self.line_width * mag_by)
        for i in range(self.total_points + 1):
            theta = 2 * math.pi * i / self.total_points
            vs = {
                    'theta': theta,
                    'time': linear_point,
                    'wave': wave_point,
                    }
            self.expr_set.eval_all(vs)
            x = vs['x'] * mag_by
            y = vs['y'] * mag_by
            if i % self.color_change_steps == 0:
                if self.color_spin:
                    t.color(
                            0.5*(1+math.sin(theta + linear_point * self.color_spin)),
                            0.5*(1+math.sin(theta + 2*math.pi/3 + linear_point * self.color_spin)),
                            0.5*(1+math.sin(theta - 2*math.pi/3 + linear_point * self.color_spin)))
                if 'width' in vs:
                    use_width = self.line_width + vs['width']
                    if use_width < 1:
                        use_width = 1.0
                    t.width(use_width * mag_by)
            if first:
                t.down()
                first = False
            t.goto(x * 100 * self.screen_size, y * 100 * self.screen_size)
        t.up()

    def draw_frame_count(self, count):
        self.draw_frame(
                (1+math.sin(2 * math.pi * count * self.wave_speed))/2,
                count * self.linear_speed)


### START: trying to save screen shots

import io
from PIL import Image

def draw_background(color):
    if not do_record:
        t.bgcolor(color)
    else:
        height = 10000
        width = 10000

        penposn = t.position()
        penstate = t.pen()

        t.penup()
        t.speed(0)  # fastest
        t.goto(-width/2-2, -height/2+3)
        t.fillcolor(color)
        t.begin_fill()
        t.setheading(0)
        t.forward(width)
        t.setheading(90)
        t.forward(height)
        t.setheading(180)
        t.forward(width)
        t.setheading(270)
        t.forward(height)
        t.end_fill()

        t.penup()
        t.setposition(*penposn)
        t.pen(penstate)

def save_screen(name):
    global mag_by

    cnv = t.getscreen().getcanvas() 
    x=1000
    y=800
    mag_by=4
    post_script = cnv.postscript(colormode = 'color', width=x*mag_by+1, height=y*mag_by+1, x=-(mag_by*x)//2, y=-(mag_by*y)//2)
    im = Image.open(io.BytesIO(post_script.encode('utf-8')))
    if mag_by != 1:
        print("save: %s"%(name))
        im = im.resize((x, y), resample = Image.ANTIALIAS)
    im.save(name + ".png", "PNG")

### END: trying to save screen shots


mag_by = 1

def run(curve_sets):
    global t

    t.penup()
    t.tracer(0)
    t.hideturtle()

    count = 0
    while True:
        t.clear()
        draw_background((0.0, 0.0, 0.0))
        for curve_set in curve_sets:
            curve_set.draw_frame_count(count)
        count += 1
        t.update()
        if do_record:
            save_screen('x.%03d'%(count-1))
            if count == do_record:
                return

args = sys.argv[1:]
curve_sets = [CurveSet(file_name) for file_name in args if not file_name.startswith('-')]
do_record=0

if '-4' in args:
    do_record=3
    mag_by = 4


run(curve_sets)

