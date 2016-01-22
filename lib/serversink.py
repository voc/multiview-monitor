#!/usr/bin/python3
import os, logging, subprocess, shlex, gi
from gi.repository import Gst, GLib

# import library components
from lib.config import Config

class ServerSink(object):
	def __init__(self):
		self.log = logging.getLogger('ServerSink')

		GLib.timeout_add_seconds(1, self.do_poll)
		self.start()

	def start(self):
		# create an ipc pipe
		self.pipe = os.pipe()

		# intervideosrc -> pipe
		pipeline = """
			matroskamux name=mux !
				fdsink fd={fd}

			intervideosrc channel=out !
				{caps} !
				queue !
				mux.
		""".format(
			caps=Config.get('output', 'caps'),
			fd=self.pipe[1],
		)

		for idx, name in enumerate(Config.options('sources')):
			pipeline += """
				interaudiosrc channel=in_a_{name} !
					{acaps} !
					queue !
					mux.audio_{idx}
			""".format(
				acaps=Config.get('input', 'audiocaps'),
				fd=self.pipe[1],
				name=name,
				idx=idx,
			)

		self.log.debug('Starting Sink-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)


		# pipe -> subprocess
		process = """
			ffmpeg
				-y
				-v warning
				-i pipe:
				-threads:0 0

				-c:v libx264
				-maxrate:v:0 5000k -bufsize:v:0 8192k -crf:0 21
				-pix_fmt:0 yuv420p -profile:v:0 main -g:v:0 25
				-preset:v:0 ultrafast
				-map 0:v

				-c:a libfdk_aac -b:a 96k -ar 44100 -ac:a 1
				-map 0:a
		"""
		for idx, name in enumerate(Config.options('sources')):
			process += """
				-metadata:s:a:{idx} title="{name}"
			""".format(
				idx=idx,
				name=name,
			)

		process += """
				-y -f mpegts {url}
		""".format(
			url=Config.get('output', 'url'),
		)

		self.log.debug('Starting Sink-Process:\n%s', process)
		self.process = subprocess.Popen(shlex.split(process),
			stdin=self.pipe[0])

	def do_poll(self):
		ret = self.process.poll()
		if ret is None:
			return True

		self.log.debug('Sink-Process died, restarting')
		self.start()
		return True
