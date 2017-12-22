#!/usr/bin/python3
import os, logging, subprocess, shlex, gi
from gi.repository import Gst, GLib

# import library components
from lib.config import Config

class CommandSink(object):
	def __init__(self, command, width, height):
		self.log = logging.getLogger('RtmpSink')
		self.command = command
		self.width = width
		self.height = height

		# create an ipc pipe
		self.pipe = os.pipe()

	def start(self):
		GLib.timeout_add_seconds(1, self.do_poll)
		self.start_process();

	def start_process(self):
		# intervideosrc -> pipe
		pipeline = """
			matroskamux name=mux !
				fdsink fd={fd}

			intervideosrc channel=out !
				video/x-raw,width={width},height={height} !
				queue !
				mux.

			audiotestsrc wave=silence !
				audio/x-raw,channels=2,rate=44100 !
				queue !
				mux.
		""".format(
			width=self.width,
			height=self.height,
			fd=self.pipe[1],
		)

		self.log.debug('Starting Sink-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)

		# pipe -> subprocess
		command = self.command.format(
			width=self.width,
			height=self.height
		)

		self.log.debug('Starting Sink-Process:\n%s', command)
		self.process = subprocess.Popen(shlex.split(command),
			stdin=self.pipe[0])

	def do_poll(self):
		ret = self.process.poll()
		if ret is None:
			return True

		self.log.debug('Sink-Process died, restarting')
		self.start()
		return True
