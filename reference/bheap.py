#!/usr/bin/python2
"""
    This file is part of CSDM.

    Copyright (C) 2013, 2014, 2015  Erika V. Jonell <@xevrem>

    CSDM is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class HeapCell(object):
	data = None
	value = None

	def __init__(self, value=None, data=None):
		self.data = data
		self.value = value

class BinaryHeap(object):

	size = 0
	length = 0
	data = []

	def __init__(self, length=16):
		self.size = 0;
		self.length = length * 2 + 2
		self.data = [None]*self.length

	def add(self, value, data):
		self.celladd(HeapCell(value,data))

	def celladd(self, bcell):
		self.size += 1

		if self.size * 2 + 1 >= self.length:
			self.grow(self.size)

		self.data[self.size] = bcell

		i = self.size

		#do any needed swapping
		while i != 1:
			if self.data[i].value <= self.data[i/2].value:
				#swap
				#print "swap {} with {}".format(self.data[i].value,self.data[i/2].value)
				temp = self.data[i/2]
				self.data[i/2] = self.data[i]
				self.data[i] = temp
				i = i/2
			else:
				break

	def removeFirst(self):
		retval = self.data[1]

		#move last item to 1st position, reduce size by one
		self.data[1] = self.data[self.size]
		self.data[self.size] = None
		self.size -= 1

		u = None
		v = 1

		while True:
			u = v

			#if both children exist
			if 2*u+1 <= self.size:
				#select lowest child
				if self.data[u].value >= self.data[2*u].value:
					v = 2*u
				if self.data[v].value >= self.data[2*u+1].value:
					v = 2*u+1
			elif 2*u <= self.size:
				if self.data[u].value >= self.data[2*u].value:
					v = 2*u

			#swap or exit?
			if u != v:
				temp = self.data[u]
				self.data[u] = self.data[v]
				self.data[v] = temp
			else:
				break #done storting

		return retval


	def grow(self, newsize):
		#print "growing heap, size: {}".format(newsize)
		newlength = newsize*2+2
		data = [None]*newlength

		for i in range(self.length):
			data[i] = self.data[i]

		self.data = data
		self.length = newlength

		#print "newlength: {}, actual: {}".format(newlength,len(self.data))


	def clear(self):
		for i in range(self.size):
			self.data[i] = None

		self.size = 0

	def getSize(self):
		return self.size
