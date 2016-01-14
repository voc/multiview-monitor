#!/usr/bin/python3
import os, logging, gi
from gi.repository import Gst

from lib.config import Config

class RtmpSink(object):
	def __init__(self):
		self.log = logging.getLogger('RtmpSink')
