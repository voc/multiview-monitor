#!/usr/bin/python3
import os, logging, subprocess, shlex, gi
from gi.repository import Gst

# import library components
from lib.config import Config

class Source(object):
	def __init__(self, name, url):
		self.log = logging.getLogger('Source[%s]' % name)
		self.url = url
		self.name = name

		# create an ipc pipe
		self.pipe = os.pipe()

		# subprocess -> pipe
		process = """
			ffmpeg
				-v warning
				-i {url}
				-filter_complex "[0:a] ebur128=video=1:meter=18 [v][a]"
				-map '[v]' -map '[a]'
				-c:v rawvideo -c:a pcm_s16le
				-pix_fmt yuv420p -r 25
				-f matroska
				pipe:
		""".format(
			url=self.url
		)

		self.log.debug('Starting Source-Process:\n%s', process)
		self.process = subprocess.Popen(shlex.split(process), stdout=self.pipe[1])


		# pipe -> this process -> intervideosink
		pipeline = """
			fdsrc fd={fd} !
			queue !
			matroskademux !
			{caps} !
			intervideosink channel=in_{name}
		""".format(
			fd=self.pipe[0],
			caps=Config.get('input', 'caps'),
			name=self.name
		)

		self.log.debug('Starting Source-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)

		# FIXME on pipeline end, kill ffmpeg and restart both
		# FIXME on ffmpeg end, kill pipeline and restart both
