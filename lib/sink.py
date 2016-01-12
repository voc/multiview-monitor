#!/usr/bin/python3
import os, logging, gi
from gi.repository import Gst

from lib.config import Config

class Sink(object):
	def __init__(self):
		self.log = logging.getLogger('Sink')

		# FIXME intervideosrc -> encoder -> rtmp(?)
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
