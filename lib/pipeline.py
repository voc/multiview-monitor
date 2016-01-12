#!/usr/bin/python3
import os, logging, subprocess
from gi.repository import Gst

# import library components
from lib.config import Config
from lib.processkeeper import ProcessKeeper

class Pipeline(object):
	"""mixing, streaming and encoding pipeline constuction and control"""

	def __init__(self):
		self.log = logging.getLogger('Pipeline')

		sources = Config.options('sources')
		if len(sources) < 1:
			raise RuntimeError("At least one Source must be configured!")

		self.mixer = self.setupVideomixer()
		self.sink = self.setupSink()
		self.sources = self.setupSources()

	def setupSources():
		sources = []
		for name, url in enumerate(Config.options('sources')):
			# FIXME put this into a class

			# create an ipc pipe
			pipe = os.pipe()

			# subprocess -> pipe
			process = subprocess.Popen("""
				ffmpeg
					-i {url}
					-filter_complex "[0:a] ebur128=video=1:meter=18 [v][a]"
					-map '[v]' -map '[a]'
					-c:v rawvideo -c:a pcm_s16le
					-pix_fmt yuv420p
					-f matroska
					pipe:
			""".format(
				url=url
			), stdout=pipe[1])

			# pipe -> this process -> intervideosink
			pipeline = """
				fdsrc fd={fd} !
				queue !
				matroskademux !
				video/x-raw !
				intervideosink channel="{name}"
			""".format(
				fd=pipe[0],
				name=name
			)

			pipelineobj = Gst.parse_launch(pipeline)
			pipelineobj.set_state(Gst.State.PLAYING)

			# on pipeline end, kill ffmpeg and restart both
			# on ffmpeg end, kill pipeline and restart both
