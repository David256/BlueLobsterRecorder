#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
import subprocess

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio, GLib, GObject

class MainWindow(Gtk.Window):
	"""La ventana principal"""

	instances = 0

	def __init__(self, title):
		super(MainWindow, self).__init__(title=title)
		# revisamos que sólo esté una instancia de esta clase
		if self.instances > 0:
			raise RuntimeError("You can not create two instances of MainWindow")
		else:
			self.instances += 1
		# algunos atributos generales
		self.title = title
		self.path_output = None
		self.subprocesses = None
		# preconfiguración
		self.set_border_width(10)
		self.set_default_size(400, 150)
		# gtk stuffs
		self.header_bar = Gtk.HeaderBar()
		self.vbox_main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.vbox_target = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.hbox_target_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		self.hbox_target_filename = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		self.vbox_preferences = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.hbox_preferences_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		self.hbox_preferences_check = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		self.hbox_preferences_frames = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		# more
		self.button_record = Gtk.Button.new_with_label("Grabar")
		self.button_stop = Gtk.Button()
		self.button_play = Gtk.Button()
		self.label_target = Gtk.Label("Destino:")
		self.entry_target = Gtk.Entry()
		self.button_explore = Gtk.Button.new_with_mnemonic("_Explorar")
		self.label_preferences = Gtk.Label("Preferencias:")
		self.check_mouse = Gtk.CheckButton("Grabar el mouse")
		self.check_audio = Gtk.CheckButton("Grabar audio")
		self.button_audio_settings = Gtk.Button.new_with_mnemonic("_Configurar Audio")
		self.label_frames = Gtk.Label("Frames por segundo:")
		self.spinbutton_frames = Gtk.SpinButton()

		# configuración gtk
		self.header_bar.props.title = self.props.title
		self.header_bar.set_show_close_button(True)
		self.spinbutton_frames.set_adjustment(Gtk.Adjustment(30, 0, 100, 1, 10, 0))

		self.button_play.add(Gtk.Image.new_from_icon_name("gtk-media-play", Gtk.IconSize.BUTTON))
		self.button_stop.add(Gtk.Image.new_from_icon_name("gtk-media-stop", Gtk.IconSize.BUTTON))
		self.header_bar.add(self.button_record)
		self.header_bar.add(self.button_play)
		self.header_bar.add(self.button_stop)
		self.set_titlebar(self.header_bar)
		# agregamos los elementos a los boxes
		self.vbox_target.add(self.hbox_target_label)
		self.vbox_target.add(self.hbox_target_filename)
		self.vbox_preferences.add(self.hbox_preferences_label)
		self.vbox_preferences.add(self.hbox_preferences_check)
		self.vbox_preferences.add(self.hbox_preferences_frames)
		self.vbox_main.add(self.vbox_target)
		self.vbox_main.add(self.vbox_preferences)
		self.add(self.vbox_main)
		# agregamos otras cosas
		self.hbox_target_label.add(self.label_target)
		self.hbox_target_filename.pack_start(self.entry_target, True, True, 0)
		self.hbox_target_filename.add(self.button_explore)
		self.hbox_preferences_label.add(self.label_preferences)
		self.hbox_preferences_check.add(self.check_mouse)
		self.hbox_preferences_check.add(self.check_audio)
		self.hbox_preferences_check.add(self.button_audio_settings)
		self.hbox_preferences_frames.add(self.label_frames)
		self.hbox_preferences_frames.add(self.spinbutton_frames)
		# conectando
		self.button_record.connect("clicked", self.on_button_record)
		self.button_stop.connect("clicked", self.on_button_stop)
		self.button_play.connect("clicked", self.on_button_play)
		self.button_explore.connect("clicked", self.on_button_explore)
		self.button_audio_settings.connect("clicked", self.on_button_audio_settings)

	def on_button_record(self, widget):
		pass

	def on_button_stop(self, widget):
		pass

	def on_button_play(self, widget):
		pass

	def on_button_explore(self, widget):
		pass

	def on_button_audio_settings(self, widget):
		pass