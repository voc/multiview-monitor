#!/usr/bin/python3
import os, logging, gi
from gi.repository import Gst

# import library components
from lib.config import Config

class Mixer(object):
	def __init__(self):
		self.log = logging.getLogger('Mixer')


		grid = Config.get('output', 'grid')
		[w, h] = [int(n) for n in grid.split('x', 1)]

		self.log.debug('Greating grid of %ux%u tiles', w, h)

		# intervideosrc(es) -> videomixer -> intervideosink
		pipeline = """
			compositor name=mix
				sink_0::xpos=0 sink_0::ypos=0
				sink_1::xpos=960 sink_1::ypos=0 !
			{caps} !
			intervideosink channel=out
		""".format(
			caps=Config.get('output', 'caps'),
		)

		for name, url in Config.items('sources'):
			pipeline += """
				intervideosrc channel=in_{name} !
					{caps} !
					textoverlay text={name} !
					mix.
			""".format(
				caps=Config.get('input', 'caps'),
				name=name
			)

		self.log.debug('Starting Mix-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)
