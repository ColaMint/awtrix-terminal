#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
屏幕阵列
"""

from font import TomThumbFont
from color import color_text


class Matrix:
    """Matrix."""
    def __init__(self, pixel_size):
        """__init__.

        :param pixel_size: 像素尺寸
        """
        self.width = 32
        self.height = 8
        self.cursor_x = 0
        self.cursor_y = 0
        self.textsize_x = 1
        self.textsize_y = 1
        self.wrap = False
        self.text_color = (0, 0, 0)
        self.text_bg_color = (0, 0, 0)
        self.pixel_size = pixel_size
        self.gfxfont = TomThumbFont()
        self.clear()

    def set_cursor(self, x, y):
        """设置光标

        :param cursor_x: X坐标
        :param cursor_y: Y坐标
        """
        self.cursor_x = x
        self.cursor_y = y

    def get_cursor_x(self):
        """获取光标的X坐标"""
        return self.cursor_x

    def get_cursor_y(self):
        """获取光标的Y坐标"""
        return self.cursor_y

    def set_text_color(self, color):
        """设置文本颜色

        :param color: RGB颜色
        """
        self.text_color = color

    def print(self, text):
        """打印文本

        :param text: 文本内容
        """
        for c in text:
            if c == '\n':
                self.cursor_x = 0
                self.cursor_y += self.gfxfont.y_advance
            elif c != '\r':
                first = self.gfxfont.first
                if ord(c) >= first and ord(c) <= self.gfxfont.last:
                    glyph = self.gfxfont.glyph[ord(c) - first]
                    w = glyph[1]
                    h = glyph[2]
                    if w > 0 and h > 0:
                        xo = glyph[4]
                        if self.wrap and ((self.cursor_x + self.textsize_x *
                                           (xo + w)) > self.width):
                            self.cursor_x = 0
                            self.cursor_y += self.textsize_y * self.gfxfont.y_advance

                    self.draw_char(self.cursor_x, self.cursor_y, ord(c),
                                   self.text_color, self.text_bg_color,
                                   self.textsize_x, self.textsize_y)
                self.cursor_x += glyph[3] * self.textsize_x

    def draw_char(self, x, y, c, color, bg, size_x, size_y):
        c -= self.gfxfont.first
        glyph = self.gfxfont.glyph[c]
        bitmap = self.gfxfont.bitmap

        bo = glyph[0]
        w = glyph[1]
        h = glyph[2]
        xo = glyph[4]
        yo = glyph[5]
        xx = 0
        yy = 0
        bits = 0
        bit = 0
        xo16 = 0
        yo16 = 0
        if size_x > 1 or size_y > 1:
            xo16 = xo
            yo16 = yo

        yy = 0
        while yy < h:
            xx = 0
            while xx < w:
                if bit & 7 == 0:
                    bits = bitmap[bo]
                    bo += 1
                bit += 1
                if bits & 0x80 != 0:
                    if size_x == 1 and size_y == 1:
                        self.draw_pixel(x + xo + xx, y + yo + yy, color)
                    else:
                        self.fill_rect(x + (xo16 + xx) * size_x,
                                       y + (yo16 + yy) * size_y, size_x,
                                       size_y, color)
                bits <<= 1
                xx += 1
            yy += 1

    def draw_pixel(self, x, y, color):
        """设置一个像素的颜色

        :param x: X坐标
        :param y: Y坐标
        :param color: RGB颜色
        """
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            self.data[x][y] = color

    def draw_circle(self, x0, y0, r, color):
        """画空心的圆

        :param x0:  圆心的X坐标
        :param y0: 圆心的Y坐标
        :param r: 半径
        :param color: RGB颜色
        """
        f = 1 - r
        ddf_x = 1
        ddf_y = -2 * r
        x = 0
        y = r

        self.draw_pixel(x0, y0 + r, color)
        self.draw_pixel(x0, y0 - r, color)
        self.draw_pixel(x0 + r, y0, color)
        self.draw_pixel(x0 - r, y0, color)

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x

            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
            self.draw_pixel(x0 + y, y0 + x, color)
            self.draw_pixel(x0 - y, y0 + x, color)
            self.draw_pixel(x0 + y, y0 - x, color)
            self.draw_pixel(x0 - y, y0 - x, color)

    def fill_circle(self, x0, y0, r, color):
        """画实心的圆

        :param x0: 圆心的X坐标
        :param y0: 圆心的Y坐标
        :param r: 半径
        :param color: RGB颜色
        """
        self.draw_fast_vline(x0, y0 - r, 2 * r + 1, color)
        self.fill_circle_helper(x0, y0, r, 3, 0, color)

    def draw_rect(self, x, y, w, h, color):
        """画空心的矩形

        :param x: 矩形左上角的X坐标
        :param y: 矩形左上角的Y坐标
        :param w: 矩形的宽度
        :param h: 矩形的高度
        :param color: RGB颜色
        """
        self.draw_fast_hline(x, y, w, color)
        self.draw_fast_hline(x, y + h - 1, w, color)
        self.draw_fast_vline(x, y, h, color)
        self.draw_fast_vline(x + w - 1, y, h, color)

    def fill_rect(self, x, y, w, h, color):
        """画实心的矩形

        :param x: 矩形左上角的X坐标
        :param y: 矩形左上角的Y坐标
        :param w: 矩形的宽度
        :param h: 矩形的高度
        :param color: RGB颜色
        """
        for i in range(w):
            for j in range(h):
                self.draw_pixel(x + i, y + j, color)

    def fill_screen(self, color):
        """以一种颜色填充整个屏幕

        :param color: RGB颜色
        """
        for x in range(self.width):
            for y in range(self.height):
                self.draw_pixel(x, y, color)

    def draw_line(self, x0, y0, x1, y1, color):
        """根据线段两端的坐标画一根线段

        :param x0: 一端的X坐标
        :param y0: 一端的Y坐标
        :param x1: 另一端的X坐标
        :param y1: 另一端的Y坐标
        :param color: RGB颜色
        """
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)

        err = dx / 2

        if y0 < y1:
            ystep = 1
        else:
            ystep = -1

        while x0 <= x1:
            if steep:
                self.draw_pixel(y0, x0, color)
            else:
                self.draw_pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def draw_fast_vline(self, x, y, h, color):
        """根据上端点和长度画一根垂直线段

        :param x: 垂直线段上端点的X坐标
        :param y: 垂直线段上端点的Y坐标
        :param h: 线段的长度
        :param color: RGB颜色
        """
        for i in range(h):
            self.draw_pixel(x, y + i, color)

    def draw_fast_hline(self, x, y, w, color):
        """根据左端点和长度画一根水平线段

        :param x: 水平线段左端点的X坐标
        :param y: 水平线段左端点的Y坐标
        :param h: 线段的长度
        :param color: RGB颜色
        """
        for i in range(w):
            self.draw_pixel(x + i, y, color)

    def fill_circle_helper(self, x0, y0, r, cornername, delta, color):
        """画实心圆

        :param x0: 圆心的X坐标
        :param y0: 圆心的Y坐标
        :param r: 半径
        :param cornername: (暂时不理解)
        :param delta:  (暂时不理解)
        :param color: RGB颜色
        """
        f = 1 - r
        ddf_x = 1
        ddf_y = -2 * r
        x = 0
        y = r

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x

            if cornername & 0x1:
                self.draw_fast_vline(x0 + x, y0 - y, 2 * y + 1 + delta, color)
                self.draw_fast_vline(x0 + y, y0 - x, 2 * x + 1 + delta, color)
            if cornername & 0x2:
                self.draw_fast_vline(x0 - x, y0 - y, 2 * y + 1 + delta, color)
                self.draw_fast_vline(x0 - y, y0 - x, 2 * x + 1 + delta, color)

    def clear(self):
        """清除整个屏幕"""
        self.data = []
        for i in range(self.width):
            self.data.append([])
            for j in range(self.height):
                self.data[i].append((0, 0, 0))

    def show(self):
        """绘制屏幕内容"""
        text = '\033[;H'
        for j in range(self.height):
            for _ in range(self.pixel_size):
                for i in range(self.width):
                    for _ in range(self.pixel_size):
                        text += color_text(self.data[i][j][0],
                                           self.data[i][j][1],
                                           self.data[i][j][2], '  ')
                text += '\n'

        text = text[:-1]
        text += '\033[39m'
        print(text, flush=True, end='')
