#!/usr/bin/python3
import os, logging, subprocess, shlex, gi
from gi.repository import Gst, GLib

# import library components
from lib.config import Config

class Source(object):
	def __init__(self, name, url):
		self.log = logging.getLogger('Source[%s]' % name)
		self.type, self.url = url.split(':', 1)
		self.name = name

		section = 'input:'+self.type
		self.width = int(Config.get(section, 'width'));
		self.height = int(Config.get(section, 'height'));
		self.command = Config.get(section, 'command');

		# create an ipc pipe
		self.pipe = os.pipe()

	def start(self):
		GLib.timeout_add_seconds(1, self.do_poll)
		self.start_process()

	def start_process(self):
		# subprocess -> pipe
		process = self.command.format(
			url=self.url,
			w=self.width,
			h=self.height
		)

		self.log.debug('Starting Source-Process:\n%s', process)
		self.process = subprocess.Popen(shlex.split(process),
			stdout=self.pipe[1])

		# pipe -> this process -> intervideosink
		pipeline = """
			fdsrc fd={fd} !
			queue !
			matroskademux !
			capssetter caps=video/x-raw,interlace-mode=progressive !
			intervideosink channel=in_{name}
		""".format(
			fd=self.pipe[0],
			name=self.name
		)

		self.log.debug('Starting Source-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)

	def stop_process(self):
		self.pipeline.set_state(Gst.State.NULL)
		self.pipeline = None

		#self.process.kill()
		self.process = None

	def do_poll(self):
		ret = self.process.poll()
		if ret is None:
			return True

		self.log.debug('Source-Process died, restarting')
		self.stop_process()
		self.start_process()
		return True
