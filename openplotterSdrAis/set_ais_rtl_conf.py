#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2020 by Sailoog <https://github.com/openplotter>
#                     e-sailing <https://github.com/e-sailing/openplotter-sdr-ais>
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

import wx, os, webbrowser, subprocess, sys, time
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-sdr-ais',currentLanguage)

		wx.Frame.__init__(self, None, title=_('Set Rtl-Sdr PPM'), size=(400,140))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-sdr-ais.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		panel = wx.Panel(self)

		self.t_value = wx.StaticText(panel, label=_('(rtl-sdr frequency correction) PPM'))
		self.value = wx.TextCtrl(panel, size=(120, 30))

		self.buttonCancel = wx.Button(panel, label=_('Cancel'))
		self.buttonCancel.Bind(wx.EVT_BUTTON, self.onButtonCancel)

		self.buttonOk = wx.Button(panel, label=_('OK'))
		self.buttonOk.Bind(wx.EVT_BUTTON, self.onButtonOk)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.buttonCancel, 0, wx.ALL, 10)
		hbox.Add(self.buttonOk, 0, wx.ALL, 10)
		


		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(self.t_value, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.Add(self.value, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.AddSpacer(20)
		#vbox.Add(self.buttonCancel, 1, wx.ALL, 5)
		#vbox.Add(self.buttonOk, 1, wx.ALL, 5)
		vbox.Add(hbox, 0, wx.ALIGN_RIGHT | wx.RIGHT, 0)
		
		panel.SetSizer(vbox)
		self.read()
		
	def read(self):
		Value = '0'
		if os.path.isfile(self.conf.home+'/.openplotter/rtl_ais.conf'):
			fo = open(self.conf.home+'/.openplotter/rtl_ais.conf', "r")
			data = fo.read().split('\n')	
			fo.close()
			
			for i in data:
				if 'PPM' in i:
					try:
						Value = i.split('=')[1]
					except: pass
			self.value.SetValue(Value)

	def write(self):	
		fo = open(self.conf.home+'/.openplotter/rtl_ais.conf', "w")
		fo.write('PPM='+self.value.GetValue()+'\n')
		fo.close()

	def onButtonCancel(self,e):
		self.Destroy()

	def onButtonOk(self,e):
		self.write()
		self.Destroy()

def main():
	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
