#!/usr/bin/python3
import os, logging, subprocess, shlex, gi
from gi.repository import Gst, GLib

# import library components
from lib.config import Config

class RtmpSink(object):
	def __init__(self, url, width, height):
		self.log = logging.getLogger('RtmpSink')
		self.url = url
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
		process = """
			ffmpeg
				-y
				-v warning
				-i pipe:
				-threads:0 0

				-c:v libx264
				-maxrate:v:0 3000k -bufsize:v:0 8192k -crf:0 21
				-pix_fmt:0 yuv420p -profile:v:0 main -g:v:0 25
				-preset:v:0 veryfast
				-map 0:v

				-strict 2 -c:a aac -b:a 96k -ar 44100 -ac:a:2 2
				-map 0:a

				-y -f flv {url}
		""".format(
			url=self.url,
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
