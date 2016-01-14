#!/usr/bin/python3
import os, logging, gi
from gi.repository import Gst

from lib.config import Config

class RtmpSink(object):
	def __init__(self):
		self.log = logging.getLogger('RtmpSink')

		# intervideosrc -> encoder -> muxer -> rtmp
		pipeline = """
			flvmux streamable=true name=mux !
				rtmpsink location="{url}"

			intervideosrc channel=out !
				videoconvert !
				x264enc !
				queue !
				mux.

			audiotestsrc wave=silence !
				audio/x-raw,channels=2,rate=44100 !
				faac !
				aacparse !
				queue !
				mux.
		""".format(
			caps=Config.get('output', 'caps'),
			url=Config.get('output', 'rtmp')
		)

		self.log.debug('Starting Sink-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)
