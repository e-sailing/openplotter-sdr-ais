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
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .version import version
else:
	import version

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(650, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-sdr-ais',currentLanguage)

		self.appsDict = []

		app = {
		'name': 'gqrx',
		'process': '',
		'show': '',
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': 'python3 '+self.currentdir+'/installGqrx.py',
		'uninstall': self.platform.admin+' apt remove -y gqrx-sdr',
		'isinstalled': 'which gqrx',
		'settings': '',
		}
		self.appsDict.append(app)

		app = {
		'name': 'welle.io',
		'process': '',
		'show': '',
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': self.platform.admin+' apt install -y welle.io',
		'uninstall': self.platform.admin+' apt remove -y welle.io',
		'isinstalled': 'which welle-io',
		'settings': '',
		}
		self.appsDict.append(app)
		
		app = {
		'name': 'pulseaudio',
		'process': '',
		'show': '',
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': 'python3 '+self.currentdir+'/installPulseaudio.py',
		'uninstall': self.platform.admin+' apt remove -y pavucontrol pulseaudio',
		'isinstalled': 'which pulseaudio',
		'settings': '',
		}
		self.appsDict.append(app)

		app = {
		'name': 'ais decoder',
		'process': 'openplotter-aisdecoder',
		'show': '',
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installAisdecoder.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallAisdecoder.py',
		'isinstalled': '/usr/local/bin/aisdecoder',
		'settings': 'python3 '+self.currentdir+'/set_ais_rtl_conf.py',
		}
		self.appsDict.append(app)

		app = {
		'name': 'rtl_ais',
		'process': 'openplotter-rtl_ais',
		'show': '',
		'edit': '',
		'included': 'no',
		'plugin': '',
		'install': self.platform.admin+' python3 '+self.currentdir+'/installRtlAis.py',
		'uninstall': self.platform.admin+' python3 '+self.currentdir+'/uninstallRtlAis.py',
		'isinstalled': '/usr/local/bin/rtl_ais',
		'settings': 'python3 '+self.currentdir+'/set_ais_rtl_conf.py',
		}
		self.appsDict.append(app)

		if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr': 
			v = version
		else: v = version.version

		wx.Frame.__init__(self, None, title=_('Sdr-Ais')+' '+v, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-sdr-ais.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(106, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		self.refreshButton = self.toolbar1.AddTool(104, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.OnRefreshButton, self.refreshButton)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.apps = wx.Panel(self.notebook)
		self.systemd = wx.Panel(self.notebook)		
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.apps, _('Apps'))
		self.notebook.AddPage(self.systemd, _('Process status'))
		self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/sdr-ais.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img0)
		self.notebook.SetPageImage(2, img1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageApps()
		self.pageSystemd()		
		self.pageOutput()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()
		
		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/sdr-ais/sdr-ais_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def pageApps(self):
		self.listApps = wx.ListCtrl(self.apps, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listApps.InsertColumn(0, _('Name'), width=320)
		self.listApps.InsertColumn(1, _('status'), width=365)
		self.listApps.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListAppsSelected)
		self.listApps.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListAppsDeselected)

		self.toolbar2 = wx.ToolBar(self.apps, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.settingsButton = self.toolbar2.AddTool(204, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings2.png"))
		self.Bind(wx.EVT_TOOL, self.OnSettingsButton, self.settingsButton)
		#self.editButton = self.toolbar2.AddTool(201, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		#self.Bind(wx.EVT_TOOL, self.OnEditButton, self.editButton)
		self.showButton = self.toolbar2.AddTool(202, _('Show'), wx.Bitmap(self.currentdir+"/data/show.png"))
		self.Bind(wx.EVT_TOOL, self.OnShowButton, self.showButton)
		self.toolbar2.AddSeparator()
		toolInstall= self.toolbar2.AddTool(203, _('Install'), wx.Bitmap(self.currentdir+"/data/install.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolInstall, toolInstall)
		toolUninstall= self.toolbar2.AddTool(205, _('Uninstall'), wx.Bitmap(self.currentdir+"/data/uninstall.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolUninstall, toolUninstall)

		self.toolbar3 = wx.ToolBar(self.apps, style=wx.TB_TEXT | wx.TB_VERTICAL)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listApps, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar2, 0)
		self.apps.SetSizer(sizer)

		self.OnRefreshApps()

	def OnRefreshButton(self, event=0):
		self.OnRefreshApps()
		self.set_listSystemd()

	def OnRefreshApps(self):
		self.notebook.ChangeSelection(0)
		self.listApps.DeleteAllItems()
		for i in self.appsDict:
			item = self.listApps.InsertItem(0, i['name'])
			if self.platform.skPort:
				installed = _('not installed')
				isinstalled = i['isinstalled'].split()
				if len(isinstalled) == 1:
					if os.path.isfile(isinstalled[0]):
						installed = _('installed')
				else:
					try:
						if len(subprocess.check_output(i['isinstalled'].split())) > 3:
							installed = _('installed')
					except: pass
				
			self.listApps.SetItem(item, 1, installed)
			if _('not installed') == installed:
				self.listApps.SetItemBackgroundColour(item,(200,200,200))
		self.onListAppsDeselected()

	def OnToolInstall(self, e):
		if self.platform.skPort: 
			index = self.listApps.GetFirstSelected()
			if index == -1: return
			apps = list(reversed(self.appsDict))
			name = apps[index]['name']
			command = apps[index]['install']
			if not command:
				self.ShowStatusBarRED(_('This app can not be installed'))
				return
			msg = _('Are you sure you want to install ')+name+_(' and its dependencies?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES:
				self.logger.Clear()
				self.notebook.ChangeSelection(2)
				popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
				for line in popen.stdout:
					if not 'Warning' in line and not 'WARNING' in line:
						self.logger.WriteText(line)
						self.ShowStatusBarYELLOW(_('Installing app, please wait... ')+line)
						self.logger.ShowPosition(self.logger.GetLastPosition())
				self.OnRefreshButton()
				#self.restart_SK(0)
			dlg.Destroy()
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def OnToolUninstall(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		name = apps[index]['name']
		command = apps[index]['uninstall']
		if not command:
			self.ShowStatusBarRED(_('This app can not be uninstalled'))
			return
		msg = _('Are you sure you want to uninstall ')+name+_(' and its dependencies?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES:
			self.logger.Clear()
			self.notebook.ChangeSelection(2)
			popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
			for line in popen.stdout:
				if not 'Warning' in line and not 'WARNING' in line:
					self.logger.WriteText(line)
					self.ShowStatusBarYELLOW(_('Uninstalling app, please wait... ')+line)
					self.logger.ShowPosition(self.logger.GetLastPosition())
			self.OnRefreshButton()
			#self.restart_SK(0)
		dlg.Destroy()

	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))

	def OnSettingsButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		command = apps[index]['settings']
		subprocess.call(command.split())

	def OnEditButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		webbrowser.open(apps[index]['edit'], new=2)

	def OnShowButton(self, e):
		index = self.listApps.GetFirstSelected()
		if index == -1: return
		apps = list(reversed(self.appsDict))
		webbrowser.open(apps[index]['show'], new=2)
		
################################################################################

	def pageSystemd(self):	
		self.started = False
		self.aStatusList = [_('inactive'),_('active')]
		self.bStatusList = [_('dead'),_('running')] 

		self.listSystemd = CheckListCtrl(self.systemd, 152)
		self.listSystemd.InsertColumn(0, _('Autostart'), width=90)
		self.listSystemd.InsertColumn(1, _('Process'), width=150)
		self.listSystemd.InsertColumn(2, _('Status'), width=150)
		self.listSystemd.InsertColumn(3, '  ', width=150)
		
		self.listSystemd.OnCheckItem = self.OnCheckItem

		self.toolbar3 = wx.ToolBar(self.systemd, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.start = self.toolbar3.AddTool(301, _('Start'), wx.Bitmap(self.currentdir+"/data/start.png"))
		self.Bind(wx.EVT_TOOL, self.onStart, self.start)
		self.stop = self.toolbar3.AddTool(302, _('Stop'), wx.Bitmap(self.currentdir+"/data/stop.png"))
		self.Bind(wx.EVT_TOOL, self.onStop, self.stop)
		self.restart = self.toolbar3.AddTool(303, _('Restart'), wx.Bitmap(self.currentdir+"/data/restart.png"))
		self.Bind(wx.EVT_TOOL, self.onRestart, self.restart)	

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listSystemd, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar3, 0)

		self.systemd.SetSizer(sizer)

		self.set_listSystemd()
		self.started = True

	def set_listSystemd(self):
		self.process = []
		for i in self.appsDict:
			if i['process'] != '':
				isinstalled = i['isinstalled'].split()
				if len(isinstalled) == 1:
					if os.path.isfile(isinstalled[0]):
						self.process.append(i['process'])
				else:
					if len(subprocess.check_output(i['isinstalled'].split())) > 50:
						self.process.append(i['process'])

		self.listSystemd.DeleteAllItems()
		index = 1
		for i in self.process:
			if i:
				index = self.listSystemd.InsertItem(sys.maxsize, '')
				self.statusUpdate(i,index)

	def statusUpdate(self, process, index): 
		command = 'systemctl show ' + process + ' --no-page'
		output = subprocess.check_output(command.split(),universal_newlines=True)
		if 'UnitFileState=enabled' in output: self.listSystemd.CheckItem(index)
		self.listSystemd.SetItem(index, 1, process)
		self.listSystemd.SetItem(index, 2, self.aStatusList[('ActiveState=active' in output)*1])
		self.listSystemd.SetItem(index, 3, self.bStatusList[('SubState=running' in output)*1])
						
	def onStart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		subprocess.call((self.platform.admin + ' systemctl start ' + self.process[index]).split())
		self.set_listSystemd()

	def onStop(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		subprocess.call((self.platform.admin + ' systemctl stop ' + self.process[index]).split())
		self.set_listSystemd()

	def onRestart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		subprocess.call((self.platform.admin + ' systemctl restart ' + self.process[index]).split())
		self.set_listSystemd()
		
	def OnCheckItem(self, index, flag):
		if not self.started: return
		if flag:
			subprocess.call((self.platform.admin + ' systemctl enable ' + self.process[index]).split())
		else:
			print(self.platform.admin + ' systemctl disable ' + self.process[index])
			subprocess.call((self.platform.admin + ' systemctl disable ' + self.process[index]).split())
		#self.set_listSystemd()

################################################################################
		

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

	def onListAppsSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.onListAppsDeselected()
		if self.listApps.GetItemBackgroundColour(i) != (200,200,200):
			self.toolbar2.EnableTool(205,True)
			apps = list(reversed(self.appsDict))
			if apps[i]['settings']: self.toolbar2.EnableTool(204,True)
			if apps[i]['edit']: self.toolbar2.EnableTool(201,True)
			if apps[i]['show']: self.toolbar2.EnableTool(202,True)
		else: self.toolbar2.EnableTool(203,True)

	def onListAppsDeselected(self, event=0):
		self.toolbar2.EnableTool(203,False)
		self.toolbar2.EnableTool(205,False)
		self.toolbar2.EnableTool(204,False)
		self.toolbar2.EnableTool(201,False)
		self.toolbar2.EnableTool(202,False)

def main():
	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
