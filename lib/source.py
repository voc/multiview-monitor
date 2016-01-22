#!/usr/bin/python3
import os, logging, subprocess, shlex, gi
from gi.repository import Gst, GLib

# import library components
from lib.config import Config

class Source(object):
	def __init__(self, name, url):
		self.log = logging.getLogger('Source[%s]' % name)
		self.url = url
		self.name = name
		self.caps = Gst.Caps.from_string(Config.get('input', 'videocaps')).get_structure(0)

		# create an ipc pipe
		self.pipe = os.pipe()

		GLib.timeout_add_seconds(1, self.do_poll)
		self.start()

	def start(self):
		w, h = self.caps.get_int('width')[1], self.caps.get_int('height')[1]

		if w < 640 or h < 480:
			raise RuntimeError('ebur128 video output-size must be at least 640x480')

		# subprocess -> pipe
		process = Config.get('input', 'command').format(
			url=self.url,
			w=w,
			h=h
		)

		self.log.debug('Starting Source-Process:\n%s', process)
		self.process = subprocess.Popen(shlex.split(process),
			stdout=self.pipe[1])

		# pipe -> this process -> intervideosink
		pipeline = """
			fdsrc fd={fd} !
				queue !
				matroskademux name=demux

			demux. !
				queue !
				{vcaps} !
				intervideosink channel=in_v_{name}

			demux. !
				queue !
				{acaps} !
				interaudiosink channel=in_a_{name}
		""".format(
			fd=self.pipe[0],
			vcaps=Config.get('input', 'videocaps'),
			acaps=Config.get('input', 'audiocaps'),
			name=self.name
		)

		self.log.debug('Starting Source-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)

	def stop(self):
		self.pipeline.set_state(Gst.State.NULL)
		self.pipeline = None

		#self.process.kill()
		self.process = None

	def do_poll(self):
		ret = self.process.poll()
		if ret is None:
			return True

		self.log.debug('Source-Process died, restarting')
		self.stop()
		self.start()
		return True
