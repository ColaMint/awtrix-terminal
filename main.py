#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import numpy
import argparse
from awtrix import Awtrix

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Awtrix终端模拟器')
    parser.add_argument('--server-host',
                        dest='server_host',
                        type=str,
                        default='localhost',
                        help='awtrix服务器域名')
    parser.add_argument('--server-port',
                        dest='server_port',
                        type=int,
                        default=7001,
                        help='awtrix服务器端口')
    parser.add_argument('--pixel-size',
                        dest='pixel_size',
                        type=int,
                        default=2,
                        help='awtrix像素尺寸')
    args = parser.parse_args()

    Awtrix(args.server_host, args.server_port, args.pixel_size)
