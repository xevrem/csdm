#!/usr/bin/python2

"""
    This file is part of CSDM.

    Copyright (C) 2013  Thomas H. Jonell <@Net_Gnome>

    CryptDistMail is free software: you can redistribute it and/or modify
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

from bheap import *
import random

def main():

	bh = BinaryHeap(50)

	for i in range(50):
		r = random.randint(0,100)
		bh.add(r,r)

	for i in range(len(bh.data)):
		print bh.removeFirst().value


if __name__ == '__main__':
	main()