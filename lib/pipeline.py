#!/usr/bin/python3
import os, logging, subprocess

# import library components
from lib.config import Config
from lib.source import Source
from lib.localsink import LocalSink
from lib.commandsink import CommandSink
from lib.mixer import Mixer

class Pipeline(object):
	def __init__(self):
		self.log = logging.getLogger('Pipeline')

	def configure(self):
		sources = Config.options('sources')
		if len(sources) < 1:
			raise RuntimeError('At least one Source must be configured!')

		self.mixer = Mixer()

		self.sources = []
		for name, url in Config.items('sources'):
			source = Source(name, url)
			self.mixer.append(source)
			self.sources.append(source)

		self.mixer.configure()

		if Config.has_option('output', 'command'):
			command = Config.get('output', 'command')
			self.sink = CommandSink(command, self.mixer.output_width, self.mixer.output_height)

		else:
			self.sink = LocalSink(self.mixer.output_width, self.mixer.output_height)

	def start(self):
		self.sink.start()
		self.mixer.start()
		for source in self.sources:
			source.start()
