#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
awtrix客户端
"""

import time
import json
import numpy
import paho.mqtt.client as mqtt
from matrix import Matrix
from color import parse_16bit_color


class Awtrix:
    """Awtrix."""
    def __init__(self, server_host, server_port, pixel_size):
        """__init__.

        :param server_host: 服务器域名
        :param server_port: 服务器端口
        :param pixel_size: 像素尺寸
        """

        self.font_x_offset = 1  # 使用TomThumb字体时需要修正的X坐标偏移量
        self.font_y_offset = 5  # 使用TomThumb字体时需要修正的Y坐标偏移量
        self.matrix = Matrix(pixel_size)
        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(server_host, server_port, 60)
        self.client.loop_forever()

    def __on_connect(self, client, userdata, flags, rc):
        client.subscribe("awtrixmatrix/#")
        client.publish("matrixClient", "connected")

    def __on_message(self, client, userdata, msg):
        self.__parse_command(msg.payload)

    def __parse_command(self, payload):
        """解析命令

        :param payload: 待解析的原始命令数据
        """
        if payload[0] == 0:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            color_r = int(payload[5])
            color_g = int(payload[6])
            color_b = int(payload[7])
            text = payload[8:].decode('ascii')
            self.matrix.set_cursor(x_coordinate + self.font_x_offset,
                                   y_coordinate + self.font_y_offset)
            self.matrix.set_text_color((color_r, color_g, color_b))
            self.matrix.print(text)
        elif payload[0] == 1:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            width = int(payload[5])
            height = int(payload[6])
            color_data = [(0, 0, 0)] * (width * height)

            i = 0
            while i < width * height * 2:
                color16 = (int(payload[i + 7]) << 8) + int(payload[i + 1 + 7])
                color_data[int(i / 2)] = parse_16bit_color(color16)
                i += 2
            for j in range(height):
                for i in range(width):
                    self.matrix.draw_pixel(x_coordinate + i, y_coordinate + j,
                                           color_data[j * width + i])
        elif payload[0] == 2:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            radius = int(payload[5])
            color_r = int(payload[6])
            color_g = int(payload[7])
            color_b = int(payload[8])
            self.matrix.draw_circle(x_coordinate, y_coordinate, radius,
                                    (color_r, color_g, color_b))
        elif payload[0] == 3:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            radius = int(payload[5])
            color_r = int(payload[5])
            color_g = int(payload[6])
            color_b = int(payload[7])
            self.matrix.fill_circle(x_coordinate, y_coordinate, radius,
                                    (color_r, color_g, color_b))
        elif payload[0] == 4:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            color_r = int(payload[4])
            color_g = int(payload[5])
            color_b = int(payload[6])
            self.matrix.draw_pixel(x_coordinate, y_coordinate,
                                   (color_r, color_g, color_b))
        elif payload[0] == 5:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            width = int(payload[5])
            height = int(payload[6])
            color_r = int(payload[7])
            color_g = int(payload[8])
            color_b = int(payload[9])
            self.matrix.draw_rect(x_coordinate, y_coordinate, width, height,
                                  (color_r, color_g, color_b))
        elif payload[0] == 6:
            x0_coordinate = int(payload[1] << 8) + int(payload[2])
            y0_coordinate = int(payload[3] << 8) + int(payload[4])
            x1_coordinate = int(payload[5] << 8) + int(payload[6])
            y1_coordinate = int(payload[7] << 8) + int(payload[8])
            color_r = int(payload[9])
            color_g = int(payload[10])
            color_b = int(payload[11])
            self.matrix.draw_line(x0_coordinate, y0_coordinate, x1_coordinate,
                                  y1_coordinate, (color_r, color_g, color_b))
        elif payload[0] == 7:
            color_r = int(payload[1])
            color_g = int(payload[2])
            color_b = int(payload[3])
            self.matrix.fill_screen((color_r, color_g, color_b))
        elif payload[0] == 8:
            self.matrix.show()
        elif payload[0] == 9:
            self.matrix.clear()
        elif payload[0] == 10:
            pass
        elif payload[0] == 11:
            pass
        elif payload[0] == 12:
            data = json.dumps({
                'type': 'MatrixInfo',
                'version': '0.01',
                'wifirssi': '0',
                'wifiquality': 200,
                'wifissid': 'unknown',
                'IP': 'unknown',
                'LUX': 0,
                'Temp': 0,
                'Hum': 0,
                'hPa': 0,
            })
            self.client.publish('matrixClient', data)
        elif payload[0] == 13:
            pass
        elif payload[0] == 14:
            pass
        elif payload[0] == 15:
            pass
            # print('[Reset]')
        elif payload[0] == 16:
            self.client.publish('matrixClient', 'ping')
        elif payload[0] == 17:
            pass
        elif payload[0] == 18:
            pass
        elif payload[0] == 19:
            pass
        elif payload[0] == 20:
            pass
        elif payload[0] == 21:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            self.matrix.set_cursor(x_coordinate + self.font_x_offset,
                                   y_coordinate + self.font_y_offset)
            data = json.loads(str(payload[2:]))
            for p in data:
                color_r = int(p['c'][0])
                color_g = int(p['c'][1])
                color_b = int(p['c'][2])
                text = p['t']
                self.matrix.set_text_color((color_r, color_g, color_b))
                self.matrix.print(text)
        elif payload[0] == 22:
            data = json.loads(str(payload))
            color_r = int(data['color'][0])
            color_g = int(data['color'][1])
            color_b = int(data['color'][2])
            scroll_speed = int(data['scrollSpeed'])
            text = data['text']

            self.matrix.set_cursor(32, 6)
            self.matrix.print(text)
            textlaenge = self.matrix.get_cursor_x() - 32
            i = 31
            while i > (-textlaenge):
                starzeit = current_milli_time()
                self.matrix.clear()
                self.matrix.set_cursor(i, 6)
                self.matrix.set_text_color((color_r, color_g, color_b))
                self.matrix.print(text)
                self.matrix.show()
                endzeit = current_milli_time()
                if (scroll_speed + starzeit - endzeit) > 0:
                    time.sleep((scroll_speed + starzeit - endzeit) / 1000)
                i -= 1
        elif payload[0] == 23:
            x_coordinate = read_short(payload[1:3])
            y_coordinate = read_short(payload[3:5])
            width = int(payload[5])
            height = int(payload[6])
            color_r = int(payload[7])
            color_g = int(payload[8])
            color_b = int(payload[9])
            self.matrix.fill_rect(x_coordinate, y_coordinate, width, height,
                                  (color_r, color_g, color_b))
        elif payload[0] == 24:
            pass
        elif payload[0] == 25:
            pass
        elif payload[0] == 26:
            pass


def current_milli_time():
    """获取毫秒时间戳"""
    return round(time.time() * 1000)


def read_short(payload):
    """从字节流中读取16位的整型

    :param payload: 字节流
    """
    return int(numpy.frombuffer(payload, numpy.dtype('>i2')))
