#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2020 by Sailoog <https://github.com/openplotter>
#                     e-sailing <https://github.com/e-sailing/openplotter-avnav>
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-sdr-ais',currentLanguage)

	platform2 = platform.Platform()
	
	if platform2.isRPI:
		rpitype = ''
		try:
			modelfile = open('/sys/firmware/devicetree/base/model', 'r', 2000)
			rpimodel = modelfile.read()[:-1]
			if rpimodel == 'Raspberry Pi Zero W Rev 1.1':
				rpitype = '0W'
			elif rpimodel == 'Raspberry Pi 2 Model B Rev 1.1':
				rpitype = '2B'
			elif rpimodel == 'Raspberry Pi 3 Model B Rev 1.2':
				rpitype = '3B'
			elif rpimodel == 'Raspberry Pi 3 Model B Plus Rev 1.3':
				rpitype = '3B+'
			elif rpimodel == 'Raspberry Pi 4 Model B Rev 1.1':
				rpitype = '4B'				
			modelfile.close()
		except: rpimodel = ''
	
	if platform2.isRPI:
		try:
			print(_('Set Jack plug 3.5 as output on the Raspberry pi...'))
			subprocess.call((platform2.admin+' amixer cset numid=3 1').split())
			print(_('DONE'))
		except Exception as e: print(_('FAILED: ')+str(e))

	try:
		print(_('Install pulseaudio...'))
		subprocess.call((platform2.admin+' apt install -y pulseaudio pavucontrol').split())
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	if platform2.isRPI:
		if rpimodel == '4B':
			try:
				print(_('Add Raspberry pi 4 settings for pulseaudio jack plug 3.5...'))
				if not os.path.isdir(conf2.home+'/.config/pulse'):
					subprocess.call(('mkdir ' + conf2.home+'/.config/pulse').split())

				file = conf2.home+'/.config/pulse/default.pa'
				if not os.path.isfile(file):	
					subprocess.call((' cp ' + currentdir + '/data/default.pa ' + conf2.home + '/.config/pulse/').split())

				print(_('DONE'))
			except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
