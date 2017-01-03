#!/usr/bin/python3
import os, logging, gi, math
from gi.repository import Gst

# import library components
from lib.config import Config

class Mixer(object):
	def __init__(self):
		self.log = logging.getLogger('Mixer')
		self.sources = []

	def append(self, source):
		self.sources.append(source)

	def configure(self):
		grid = Config.get('output', 'grid')
		grid_width, grid_height = [int(n) for n in grid.split('x', 1)]

		self.log.info('Configuring grid of %ux%u tiles', grid_width, grid_height)

		# intervideosrc(es) -> videomixer -> intervideosink
		pipeline = """
			compositor name=mix
		"""

		pos_x = 0
		pos_y = 0

		col_w = 0
		for tile_x in range(0, grid_width):
			pos_y = 0
			pos_x += col_w
			col_w = 0

			self.log.debug('')

			for tile_y in range(0, grid_height):
				index = tile_x * grid_height + tile_y

				source = self.sources[index]
				self.log.debug('Placing tile #%2u %u/%u of type %10s (size: %4u/%4upx) at %4u/%4upx in the viewport',
					index, tile_x, tile_y,
					source.type, source.width, source.height,
					pos_x, pos_y)

				pos_y += source.height
				col_w = max(col_w, source.width)

				# txpx, typx = tx*tw, ty*th
				# self.log.debug('Placing tile #%u %u/%u at %u/%upx in the viewport', idx, tx, ty, txpx, typx)
				# pipeline += """
				# 	sink_{idx}::xpos={x} sink_{idx}::ypos={y} sink_{idx}::width={w} sink_{idx}::height={h}
				# """.format(
				# 	idx=idx,
				# 	x=txpx,
				# 	y=typx,
				# 	w=tw,
				# 	h=th,
				# )

		self.log.debug('')

		output_width = pos_x + col_w
		output_height = pos_y
		self.log.info('Calculated final grid-size to be %ux%upx',
			output_width, output_height)


		pipeline += """
			intervideosink channel=out
		""".format(
		)

		for name, url in Config.items('sources'):
			pipeline += """
				intervideosrc channel=in_{name} !
					textoverlay text={name} font-desc="Normal 40"!
					mix.
			""".format(
				name=name
			)

		self.log.debug('Configured Mix-Pipeline:\n%s', pipeline)
		self.pipeline = Gst.parse_launch(pipeline)


	def start(self):
		self.log.debug('Starting Mix-Pipeline')
		self.pipeline.set_state(Gst.State.PLAYING)
