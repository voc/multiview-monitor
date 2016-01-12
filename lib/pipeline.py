#!/usr/bin/python3
import os, logging, subprocess

# import library components
from lib.config import Config
from lib.source import Source
from lib.sink import Sink
from lib.mixer import Mixer

class Pipeline(object):
	def __init__(self):
		self.log = logging.getLogger('Pipeline')

		sources = Config.options('sources')
		if len(sources) < 1:
			raise RuntimeError('At least one Source must be configured!')

		self.mixer = Mixer()
		self.sink = Sink()

		self.sources = []
		for name, url in Config.items('sources'):
			self.sources.append(Source(name, url))

