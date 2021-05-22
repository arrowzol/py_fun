#!/usr/local/bin/python3

import sys
import functools as ft
import itertools as it
import math
import turtle as t
import re
from time import sleep
import expr

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
        t.up()
        first = True
        t.width(self.line_width)
        for i in range(self.total_points + 1):
            theta = 2 * math.pi * i / self.total_points
            vs = {
                    'theta': theta,
                    'time': linear_point,
                    'wave': wave_point,
                    }
            self.expr_set.eval_all(vs)
            x = vs['x']
            y = vs['y']
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
                    t.width(use_width)
            if first:
                t.down()
                first = False
            t.goto(x * 100 * self.screen_size, y * 100 * self.screen_size)
        t.up()

    def draw_frame_count(self, count):
        self.draw_frame(
                (1+math.sin(2 * math.pi * count * self.wave_speed))/2,
                count * self.linear_speed)

def run(curve_sets):
    global t

    t.bgcolor(0.0, 0.0, 0.0)
    t.tracer(0)
    t.hideturtle()

    count = 0
    while True:
        t.clear()
        for curve_set in curve_sets:
            curve_set.draw_frame_count(count)
        count += 1
        t.update()

args = sys.argv[1:]
curve_sets = [CurveSet(file_name) for file_name in args]
run(curve_sets)

load_json()
run()

