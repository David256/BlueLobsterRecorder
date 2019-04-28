#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gi.repository import GLib
import io
import os
import pydbus
import subprocess
import time

def create_temp_from(path, ext=""):
	return "/tmp/" + os.path.basename(path) + ext

class Recorder(object):
	"""El grabador bajo Wayland"""
	def __init__(self, logger, enable_audio=False, enable_mouse=False):
		super(Recorder, self).__init__()
		self.logger = logger
		self.enable_audio = enable_audio
		self.enable_mouse = enable_mouse
		self.dbus = pydbus.SessionBus()
		self.shell_screencast = self.dbus.get("org.gnome.Shell.Screencast", "/org/gnome/Shell/Screencast")
		self.processes = list()
		self.filename = None
	
	def record(self, filename, frames, audio_devices=[]):
		self.logger.debug("Nueva grabación: " + filename)
		self.logger.debug("frames=" + str(frames))
		self.logger.debug("audio_devices=" + (", ".join(audio_devices)))
		self.filename = filename
		if self.enable_audio:
			for audio_device in audio_devices:
				comand = [
					"ffmpeg",
					"-f", "pulse",
					"-y", "-i",
					audio_device,
					"/tmp/_blue_lobster_{stuff}.mkv".format(stuff=audio_device),
					#"-loglevel", "panic"
				]
				process = subprocess.Popen(comand, stderr=open("/dev/null", "wb"))
				self.processes.append(process)

		self.shell_screencast.Screencast(
			create_temp_from(self.filename, ".webm"),
			{
				"framerate": GLib.Variant("i", frames),
				"draw-cursor": GLib.Variant("b", self.enable_mouse),
				"pipeline": GLib.Variant("s", "vp8enc min_quantizer=10 max_quantizer=50 cq_level=13 cpu-used=5 deadline=1000000 threads=%T ! queue ! webmmux")
			})

	def stop(self):
		self.logger.info("Se ha parado la grabación")
		if not self.filename:
			raise RuntimeError("No se puede parar la grabación porque no está iniciada grabando en un archivo")
		self.shell_screencast.StopScreencast()
		for process in self.processes:
			process.terminate()

	def mix(self, filename):
		self.logger.debug("Comenzando el mezclaje: " + filename)
		if os.path.exists(filename):
			os.remove(filename)
		fio_w = io.FileIO(filename, "w")
		fio_r = io.FileIO(filename, "r")
		if self.enable_audio:
			if os.path.exists(filename):
				os.remove(filename)
			fio_w = io.FileIO(filename, "w")
			fio_r = io.FileIO(filename, "r")
			# unimos primero el audio, si se permite
			comand = ["ffmpeg", "-y"]
			if len(self.processes) > 1:
				comand.extend([
					"-filter_complex", "amerge",
					"-ac", "2",
					#"-c:a", "libmp3lame",
					#"-q:a", "4"
				])
			for process in self.processes:
				comand.extend([
					"-i",
					"/tmp/_blue_lobster_{stuff}.mkv".format(
						stuff=process.args[5])])
			comand.append("/tmp/_blue_lobster_audio.mkv")
			if self.processes:
				self.logger.debug(comand)
				process = subprocess.Popen(comand, stderr=fio_w)
				yield "Mezclando audios...", process, fio_r
				code = process.wait()
				if code:
					self.logger.error("Código retornado 1th: " + str(code))
					raise RuntimeError("Tengo problemas al unir archivos de audio")
		# ahora unimos todo el audio al vídeo
		comand = [
			"ffmpeg", "-y",
			"-i", create_temp_from(self.filename, ".webm")
		]
		if self.enable_audio:
			comand.extend(["-i", "/tmp/_blue_lobster_audio.mkv"])
		comand.append(self.filename)
		self.logger.debug(comand)
		process = subprocess.Popen(comand, stderr=fio_w)
		yield "Mezclando vídeo..", process, fio_r
		code = process.wait()
		if code:
			self.logger.error("Código retornado 2th: " + str(code))
			raise RuntimeError("Tengo problemas al unir archivos de vídeo con audio")
		yield "Finalizando", None, None