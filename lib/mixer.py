#!/usr/bin/python3
import os, logging, gi, math
from gi.repository import Gst

# import library components
from lib.config import Config

class Mixer(object):
	def __init__(self):
		self.log = logging.getLogger('Mixer')

		caps = Gst.Caps.from_string(Config.get('output', 'caps')).get_structure(0)
		ow, oh = caps.get_int('width')[1], caps.get_int('height')[1]

		grid = Config.get('output', 'grid')
		gw, gh = [int(n) for n in grid.split('x', 1)]

		tw, th = math.floor(ow / gw), math.floor(oh / gh)

		self.log.info('Greating grid of %ux%u tiles with %ux%upx each to fill a viewport of %ux%upx', gw, gh, tw, th, ow, oh)

		# FIXME calculate actual positions ;)
		# intervideosrc(es) -> videomixer -> intervideosink
		pipeline = """
			compositor name=mix
		"""
		for tx in range(0, gw):
			for ty in range(0, gh):
				idx = tx*gh+ty
				txpx, typx = tx*tw, ty*th
				self.log.debug('Placing tile #%u %u/%u at %u/%upx in the viewport', idx, tx, ty, txpx, typx)
				pipeline += """
					sink_{idx}::xpos={x} sink_{idx}::ypos={y} sink_{idx}::width={w} sink_{idx}::height={h}
				""".format(
					idx=idx,
					x=txpx,
					y=typx,
					w=tw,
					h=th,
				)

		pipeline += """
			! {caps} !
			intervideosink channel=out
		""".format(
			caps=Config.get('output', 'caps'),
		)

		for name, url in Config.items('sources'):
			pipeline += """
				intervideosrc channel=in_v_{name} !
					{vcaps} !
					textoverlay text={name} font-desc="Normal 40"!
					mix.
			""".format(
				vcaps=Config.get('input', 'videocaps'),
				name=name
			)

		self.log.debug('Starting Mix-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)
		self.pipeline.set_state(Gst.State.PLAYING)
