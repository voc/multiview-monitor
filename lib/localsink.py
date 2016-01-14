#!/usr/bin/python3
import os, logging, gi
from gi.repository import Gst

from lib.config import Config
from lib.mainloop import MainLoop

class LocalSink(object):
	def __init__(self):
		self.log = logging.getLogger('LocalSink')

		# FIXME intervideosrc -> encoder -> display
		pipeline = """
			intervideosrc channel=out !
			{caps} !
			videoconvert !
			xvimagesink
		""".format(
			caps=Config.get('output', 'caps')
		)

		self.log.debug('Starting Sink-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)

		self.log.debug('Binding End-of-Stream-Signal on Sink-Pipeline')
		self.pipeline.bus.add_signal_watch()
		self.pipeline.bus.connect("message::eos", self.on_eos)

	def on_eos(self, bus, message):
		self.log.debug('Received End-of-Stream-Signal on Source-Pipeline, shutting down')
		MainLoop.quit()
