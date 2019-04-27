#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gi.repository import GLib
import os
import pydbus
import subprocess
import time

AUDIO_ERROR = 0x05
VIDEO_ERROR = 0x07
SUCCESSFUL  = 0x09

def create_temp_from(path, ext=""):
	return "/tmp/" + os.path.basename(path) + ext

class Recorder(object):
	"""El grabador bajo Wayland"""
	def __init__(self, enable_audio=False, enable_mouse=False):
		super(Recorder, self).__init__()
		self.enable_audio = enable_audio
		self.enable_mouse = enable_mouse
		self.dbus = pydbus.SessionBus()
		self.shell_screencast = self.dbus.get("org.gnome.Shell.Screencast", "/org/gnome/Shell/Screencast")
		self.processes = list()
		self.filename = None
	
	def record(self, filename, frames, audio_devices=[]):
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
				process = subprocess.Popen(comand)
				self.processes.append(process)

		self.shell_screencast.Screencast(
			create_temp_from(self.filename, ".webm"),
			{
				"framerate": GLib.Variant("i", frames),
				"draw-cursor": GLib.Variant("b", self.enable_mouse),
				"pipeline": GLib.Variant("s", "vp8enc min_quantizer=10 max_quantizer=50 cq_level=13 cpu-used=5 deadline=1000000 threads=%T ! queue ! webmmux")
			})

	def stop(self):
		if not self.filename:
			raise RuntimeError("No se puede parar la grabación porque no está iniciada grabando en un archivo")
		self.shell_screencast.StopScreencast()
		for process in self.processes:
			process.terminate()
		time.sleep(1)
		result = self._join()
		if result == AUDIO_ERROR:
			raise RuntimeError("Tengo problemas al unir archivos de audio")
		elif result == VIDEO_ERROR:
			raise RuntimeError("Tengo problemas al unir archivos de vídeo con audio")
		else:
			print("files joined")

	def _join(self):
		if self.enable_audio:
			# unimos primero el audio, si se permite
			comand = [
				"ffmpeg",
				"-filter_complex", "amerge",
				"-y", "-ac", "2",
				#"-c:a", "libmp3lame",
				#"-q:a", "4"
			]
			for process in self.processes:
				comand.extend([
					"-i",
					"/tmp/_blue_lobster_{stuff}.mkv".format(
						stuff=process.args[5])])
			comand.append("/tmp/_blue_lobster_audio.mkv")
			code = subprocess.call(comand)
			if code:
				return AUDIO_ERROR
		# ahora unimos todo el audio al vídeo
		comand = [
			"ffmpeg", "-y",
			"-i", create_temp_from(self.filename, ".webm")
		]
		if self.enable_audio:
			comand.extend(["-i", "/tmp/_blue_lobster_audio.mkv"])
		comand.append(self.filename)
		code = subprocess.call(comand)
		if code:
			return VIDEO_ERROR
		return SUCCESSFUL