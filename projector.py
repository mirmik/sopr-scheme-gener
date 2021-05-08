import numpy
import math

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def deg(x): return x / 180.0 * math.pi

class Projector:
	def update_matrix(self):
		if self.iso_projection:
			self.matrix = numpy.matrix([
				[           1,     -math.cos(self.pitch)*self.zmul,           0, self.mov_x],
				[           0,                     1,           0, self.mov_y],
				[           0,     +math.sin(self.pitch)*self.zmul,          1, self.mov_z],
				[           0,                     0,           0,          1]
			])
			return


		t = numpy.matrix([
			[1,0,0,self.mov_x],
			[0,1,0,self.mov_y],
			[0,0,1,self.mov_z],
			[0,0,0,1]
		])

		a=self.yaw
		m0 = numpy.matrix([
			[math.cos(a),-math.sin(a),0,0],
			[math.sin(a),math.cos(a),0,0],
			[0,0,1,0],
			[0,0,0,1]
		])

		b=self.pitch
		m1 = numpy.matrix([
			[1,0,0,0],
			[0,math.cos(b),-math.sin(b),0],
			[0,math.sin(b),math.cos(b),0],
			[0,0,0,1]
		])
		
		self.matrix = t * m1 * m0

	def __init__(self):
		self.iso_projection = False
		self.pitch=deg(-30)
		self.yaw=deg(30)
		self.mov_x = 0
		self.mov_y = 0
		self.mov_z = 0
		self.update_matrix()

	def set_iso_projection(self, en=True):
		self.iso_projection=en
		self.update_matrix()

	def set_zmul(self, zmul):
		self.zmul = zmul
		self.update_matrix()

	def set_pitch(self, pitch):
		self.pitch = pitch
		self.update_matrix()

	def set_yaw(self, yaw):
		self.yaw = yaw
		self.update_matrix()

	def set_mov(self, x, y):
		self.mov_x = x
		self.mov_y = y
		self.update_matrix()

	def project(self, x, y, z):
		vec = self.matrix * numpy.array([[x], [y], [z], [1]])
		return QPointF(vec[0], -vec[2])

	def __call__(self, *args):
		if len(args) == 1:
			return self.project(args[0][0], args[0][1], args[0][2])
		return self.project(*args)