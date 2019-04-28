#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
import os
import subprocess
import threading

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio, GLib, GObject

from classes.gui.window import MainWindow, ExplorerWindow, AudioSettinsWindow
from classes.recorder import Recorder

class GUI(MainWindow):
	"""El controlador de la GUI"""
	def __init__(self, title):
		super(GUI, self).__init__(title)
		self.recorder = None
		self.path_output = None
		self.audio_devices = list()
		self.button_stop.set_sensitive(False)
		self.button_play.set_sensitive(False)
		self.button_audio_settings.set_sensitive(False)

	def on_button_record_clicked(self, widget):
		if not self.recorder is None:
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="La grabación está corriendo ya",
				use_markup=False,
				type=Gtk.MessageType.WARNING,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("Ya estoy grabando, no puedes grabar sobre la grabación en curso...")
			response = message_dialog.run()
			message_dialog.destroy()
			return None
		if not self.entry_target.get_text():
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="No se ha especificado la ruta para guardar",
				use_markup=False,
				type=Gtk.MessageType.WARNING,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("Necesito la ruta para guardar el vídeo que grabaré, escriba la ruta o explore.")
			response = message_dialog.run()
			message_dialog.destroy()
			return None
		if not os.access(os.path.dirname(self.entry_target.get_text()), os.W_OK):
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="La ruta establecida no es escribible",
				use_markup=False,
				type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("En la ruta establecida no tenemos permiso de escritura.")
			response = message_dialog.run()
			message_dialog.destroy()
			return None
		self.recorder = Recorder(
			enable_audio=self.check_audio.get_active(),
			enable_mouse=self.check_mouse.get_active())
		self.recorder.record(
			filename=self.entry_target.get_text(),
			frames=self.spinbutton_frames.get_numeric(),
			audio_devices=self.audio_devices)
		# bloqueamos los botones
		self.button_explore.set_sensitive(False)
		self.button_record.set_sensitive(False)
		self.entry_target.set_sensitive(False)
		self.check_mouse.set_sensitive(False)
		self.check_audio.set_sensitive(False)
		self.button_audio_settings.set_sensitive(False)
		self.spinbutton_frames.set_sensitive(False)
		self.button_play.set_sensitive(False)
		self.button_stop.set_sensitive(True)

	def on_button_stop_clicked(self, widget):
		if not self.recorder:
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="No se está grabando nada",
				use_markup=False,
				type=Gtk.MessageType.WARNING,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("Priimero debes comenzar a grabar...")
			response = message_dialog.run()
			message_dialog.destroy()
			return None

		# finalizando la grabación procesando lo grabado
		message_dialog = Gtk.MessageDialog(
			parent=self,
			text="Procesando los archivos...",
			use_markup=False,
			type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			modal=True)
		message_dialog.format_secondary_text("Por favor espera, tenemos que unir/formatear partes.")
		def _(message_dialog):
			try:
				self.recorder.stop()
			except Exception as e:
				message_dialog = Gtk.MessageDialog(
					parent=self,
					text="Error al procesar archivos grabados",
					use_markup=False,
					type=Gtk.MessageType.ERROR,
					buttons=Gtk.ButtonsType.OK,
					modal=True)
				message_dialog.format_secondary_text(str(e))
				response = message_dialog.run()
				message_dialog.destroy()
				return None
			else:
				self.recorder = None
			# volvemos todo a la normalidad
			self.button_explore.set_sensitive(True)
			self.button_record.set_sensitive(True)
			self.entry_target.set_sensitive(True)
			self.check_mouse.set_sensitive(True)
			self.check_audio.set_sensitive(True)
			self.button_audio_settings.set_sensitive(True)
			self.spinbutton_frames.set_sensitive(True)
			self.button_play.set_sensitive(True)
			self.button_stop.set_sensitive(False)
			message_dialog.destroy()
		threading.Thread(target=_, args=(message_dialog,)).start()
		response = message_dialog.run()
		message_dialog.destroy()

	def on_button_play_clicked(self, widget):
		# comprobamos que no se está grabando
		if not self.recorder is None:
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="No se ha terminado de grabar",
				use_markup=False,
				type=Gtk.MessageType.WARNING,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("Primero pare la grabación antes de reproducirla")
			response = message_dialog.run()
			message_dialog.destroy()
			return None
		# comprobamos que se tiene una ruta establecida
		if not self.path_output:
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="No se ha definido la ruta del archivo",
				use_markup=False,
				type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("Primero proporcione la ruta para guardar el archivo.")
			response = message_dialog.run()
			message_dialog.destroy()
			return None
		# comprobamos que el archivo establecido se puede leer
		if not os.access(self.path_output, os.R_OK):
			message_dialog = Gtk.MessageDialog(
				parent=self,
				text="No se puede leer el archivo",
				use_markup=False,
				type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.OK,
				modal=True)
			message_dialog.format_secondary_text("El archivo %s no se puede leer." % self.path_output)
			response = message_dialog.run()
			message_dialog.destroy()
			return None
		# llamamos por ayuda...
		message_dialog = Gtk.MessageDialog(
			parent=self,
			text="Abriendo...",
			use_markup=False,
			type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			modal=True)
		message_dialog.format_secondary_text("Por favor espera, abriendo.")
		def _(message_dialog):
			code = subprocess.call(["xdg-open", self.path_output])
			message_dialog.destroy()
			if code:
				message_dialog = Gtk.MessageDialog(
					parent=self,
					text="Abrir el archivo ha devuelto error",
					use_markup=False,
					type=Gtk.MessageType.ERROR,
					buttons=Gtk.ButtonsType.OK,
					modal=True)
				message_dialog.format_secondary_text("Código de error %d retornado." % code)
				response = message_dialog.run()
				message_dialog.destroy()
		threading.Thread(target=_, args=(message_dialog,)).start()
		response = message_dialog.run()
		message_dialog.destroy()

	def on_button_explore_clicked(self, widget):
		explorer_window = ExplorerWindow(self)
		path = explorer_window.explore()
		if path:
			self.path_output = path
			self.entry_target.set_text(self.path_output)

	def on_button_audio_settings_clicked(self, widget):
		audio_settings_window = AudioSettinsWindow(self)
		response = audio_settings_window.run()
		audio_settings_window.destroy()
		if response == Gtk.ResponseType.OK:
			self.audio_devices = audio_settings_window.audio_devices
			print("Fijando los dispositivos:")
			[print(dev) for dev in self.audio_devices]

	def on_check_audio_toggled(self, widget):
		self.button_audio_settings.set_sensitive(self.check_audio.get_active())

	def on_entry_target_changed(self, widget):
		self.path_output = widget.get_text()