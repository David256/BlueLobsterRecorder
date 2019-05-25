#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
import os
import re
import time
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
		self.button_record.connect("clicked", self.on_button_record_clicked)
		self.button_stop.connect("clicked", self.on_button_stop_clicked)
		self.button_play.connect("clicked", self.on_button_play_clicked)
		self.button_explore.connect("clicked", self.on_button_explore_clicked)
		self.button_audio_settings.connect("clicked", self.on_button_audio_settings_clicked)
		self.check_mouse.connect("toggled", self.on_check_mouse_toggled)
		self.check_audio.connect("toggled", self.on_check_audio_toggled)
		self.entry_target.connect("changed", self.on_entry_target_changed)

	def on_button_record_clicked(self, widget):
		pass

	def on_button_stop_clicked(self, widget):
		pass

	def on_button_play_clicked(self, widget):
		pass

	def on_button_explore_clicked(self, widget):
		pass

	def on_button_audio_settings_clicked(self, widget):
		pass

	def on_check_mouse_toggled(self, widget):
		pass

	def on_check_audio_toggled(self, widget):
		pass

	def on_entry_target_changed(self, widget):
		pass

class ExplorerWindow(Gtk.FileChooserDialog):
	"""La ventana del explorador de archivo"""
	def __init__(self, parent=None):
		super(ExplorerWindow, self).__init__(
			parent=parent,
			title="Guardar en:",
			action=Gtk.FileChooserAction.SAVE)
		self.logger = parent.logger
		self.path = None
		self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		self.add_button(Gtk.STOCK_SAVE_AS, Gtk.ResponseType.OK)
		self.filter_text = Gtk.FileFilter()
		self.filter_text.set_name("Archivo de vídeo")
		self.filter_text.add_mime_type("video/mp4")
		self.filter_text.add_mime_type("video/mkv")
		self.filter_text.add_mime_type("video/webm")
		self.add_filter(self.filter_text)

	def explore(self):
		self.logger.info("Se pide explorar")
		response = self.run()
		if response == Gtk.ResponseType.OK:
			filename = self.get_filename()
			# si ya existe, preguntamos
			if os.path.exists(filename):
				message_dialog = Gtk.MessageDialog(
					parent=self,
					text="El archivo %s ya existe, ¿Quiere sobreescribirlo?" % os.path.basename(filename),
					use_markup=False,
					type=Gtk.MessageType.WARNING,
					buttons=Gtk.ButtonsType.YES_NO,
					modal=True)
				message_dialog.format_secondary_text(
					"Si sobreescribes, todo el contenido del archivo será borrado " +
					"para remplazarlo con el nuevo contenido.")
				response2 = message_dialog.run()
				message_dialog.destroy()
				# entonces, revisamos qué quiere el usuario
				if response2 == Gtk.ResponseType.NO:
					message_dialog.destroy()
					return self.explore()
				else:
					self.path = filename
					message_dialog.destroy()
					self.destroy()
					return self.path
			else:
				self.path = filename
				self.destroy()
				return self.path
		elif response == Gtk.ResponseType.CANCEL:
			self.destroy()
			return self.path

class AudioSettinsWindow(Gtk.Dialog):
	"""La ventana que pregunta por más información para configurar la grabación de audio."""
	def __init__(self, parent=None):
		super(AudioSettinsWindow, self).__init__(
			title="Configuración de audio",
			parent=parent,
			flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
		self.logger = parent.logger
		self._audio_devices = set()
		self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
		self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		# configuramos un par de cosas
		self.set_border_width(10)
		self.set_default_size(350, 300)
		# personalizamos este diálogo
		self.vbox_main = self.get_content_area()
		self.vbox_devices = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.frame = Gtk.Frame()
		# las cosas se agregan
		self.vbox_main.add(Gtk.Label("Seleccione el/los dispositivo(s) de audio."))
		self.vbox_main.add(self.frame)
		# buscamos los dispositivos de audio
		for description, name in self._get_audio_devices().items():
			text = description + "\n"
			text += "(" + name + ")"
			self.logger.debug("Obtenido: "  + text)
			check_audio_device = Gtk.CheckButton(text)
			check_audio_device.connect("toggled", self.on_check_audio_devices_toggled, name)
			self.vbox_devices.add(check_audio_device)
		# vamos terminando
		self.frame.add(self.vbox_devices)
		self.frame.set_label("los dispositivos:")
		self.show_all()
	
	def _get_audio_devices(self):
		output = subprocess.check_output(["pacmd", "list-sources"])
		name_devices = re.findall("name: <(.*)>", output.decode())
		description_devices = re.findall("device.description = \"(.*)\"", output.decode())
		return {description: name for description, name in zip(description_devices, name_devices)}

	def on_check_audio_devices_toggled(self, widget, name):
		if widget.get_active():
			self._audio_devices.add(name)
		else:
			self._audio_devices.remove(name)

	@property
	def audio_devices(self):
		return list(self._audio_devices)

class ProgressWindow(Gtk.Dialog):
	"""La ventana que muestra qué tal va el procesamiento de los archivos"""
	def __init__(self, parent):
		super(ProgressWindow, self).__init__(
			self,
			parent=parent,
			title="Procesando archivos...",
			flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
		self.logger = parent.logger
		self.process = None
		self.std = None
		self.cancelled = False
		self.destroyed = False
		self.re_duration = re.compile(r"Duration: (\d\d):(\d\d):(\d\d(\.\d\d))")
		self.re_time = re.compile(r"time=(\d\d):(\d\d):(\d\d\.\d\d)")
		# agregamos un botón
		self.add_button(Gtk.STOCK_STOP, Gtk.ResponseType.CANCEL)
		# configuramos un par de cosas
		self.set_border_width(10)
		self.set_default_size(350, 100)
		# personalizamos este diálogo
		self.vbox_main = self.get_content_area()
		self.progress = Gtk.ProgressBar()
		self.label_info = Gtk.Label()
		# las cosas se agregan
		self.vbox_main.add(self.label_info)
		self.vbox_main.add(self.progress)
		# agregamos un conector a eventos
		self.connect("destroy", self._destroy_callback)
		self.show_all()

	def _destroy_callback(self, widget):
		self.destroyed = True

	def check(self, process, std, info):
		self.logger.debug("Nuevo trabajo para: " + info)
		self.process = process
		self.std = std
		duration = -1
		self.label_info.set_text(info)
		self.progress.set_fraction(0.0)
		buffer = str()
		while self.process.poll() is None:
			content = self.std.read()
			content = content.decode()
			content = content.replace("\r", "\n")
			if content:
				buffer += content
				if duration < 0:
					matched = self.re_duration.search(buffer)
					if matched:
						numbers = list(matched.groups())[:3]
						numbers.reverse()
						duration = sum([float(number)*(60**i) for i,number in enumerate(numbers)])
						self.logger.debug("La duration: " + str(duration))

						# revisamos el otro a ver
						matched = self.re_time.search(buffer)
						if matched:
							GLib.idle_add(self.update_progress, fraction=1.0)
							self.logger.debug("Ya estaba finalizado")
							break

					continue
				#self.logger.debug("La duration: " + str(duration))
				if duration > 0:
					matched = self.re_time.findall(buffer)
					matched.reverse()
					matched = matched[:-1]
					if matched:
						numbers = list(matched[0])[:3]
						numbers.reverse()
						time = sum([float(number)*(60**i) for i,number in enumerate(numbers)])
						fraction = time / duration
						self.logger.debug("Valor time: " + str(time) + " > " + str(numbers) + " = " + str(fraction))
						GLib.idle_add(self.update_progress, fraction)
				buffer = buffer[:-50]
		return self.process.poll()

	def cancel(self):
		# cancela el actual proceso
		self.logger.info("Se cancela el progreso")
		self.process.terminate()
		self.cancelled = True

	def update_progress(self, fraction):
		self.progress.set_fraction(fraction)