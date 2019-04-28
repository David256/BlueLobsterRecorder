#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from classes.gui import GUI

gui = GUI("Blue Lobster Recorder")
gui.connect("destroy", Gtk.main_quit)
gui.show_all()

Gtk.main()