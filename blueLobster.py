#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from classes.gui import GUI

file = open("/tmp/BlueLobsterRecorder.log", "w")

logger = logging.getLogger("BlueLobsterRecorder")
formatter = logging.Formatter("%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: \"%(message)s\"")

console_output_handler = logging.StreamHandler(file)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

logger.setLevel(logging.DEBUG)

logger.debug("Comenzamos")

gui = GUI("Blue Lobster Recorder", logger)
gui.connect("destroy", Gtk.main_quit)
gui.show_all()

Gtk.main()

file.close()