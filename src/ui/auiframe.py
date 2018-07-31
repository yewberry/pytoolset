import wx
import wx.lib.agw.aui as aui
from wx.lib.agw.aui import aui_switcherdialog as ASD

import wx.adv
from version import VER

import zw.images as images
import zw.logger as logger

import ui.ids as ids
from ui.ippool.ippool import IPPoolPerspective
from ui.sizereportctrl import SizeReportCtrl

LOG = logger.getLogger(__name__)

ID_MY_CUST = wx.ID_HIGHEST + 1
ID_SWITCH_PANE = ID_MY_CUST
ID_IPPOOL_START = ID_MY_CUST + 1
ID_IPPOOL_VALID = ID_MY_CUST + 2
ID_CUST_TOOLBAR = ID_MY_CUST + 3

class AuiFrame(wx.Frame):

	def __init__(self, parent, id=wx.ID_ANY, title="", pos= wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE|wx.SUNKEN_BORDER, log=None):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)

		self._mgr = aui.AuiManager()
		# tell AuiManager to manage this frame
		self._mgr.SetManagedWindow(self)
		self.perspectives = []
		self.perspectives.append(IPPoolPerspective(self, self._mgr))
		self.tb = None

		self.create_menubar()
		self.create_toolbar()
		self.create_statusbar()
		self.create_panes()
		self.bind_events()
		self.SetIcon(images.zhao.GetIcon())

	def create_menubar(self):
		# create menu
		mb = wx.MenuBar()
		file_menu = wx.Menu()
		if wx.Platform == "__WXMAC__":
			switcherAccel = "Alt+Tab"
		elif wx.Platform == "__WXGTK__":
			switcherAccel = "Ctrl+/"
		else:
			switcherAccel = "Ctrl+Tab"
		file_menu.Append(ID_SWITCH_PANE, _("S&witch Window...") + "\t" + switcherAccel)
		file_menu.Append(wx.ID_EXIT, _('Exit'))
		mb.Append(file_menu, _('File'))

		for p in self.perspectives:
			menu_arr = p.create_menu()
			for m in menu_arr:
				title = m['title']
				menu = m['menu']
				mb.Append(menu, title)
		
		self.SetMenuBar(mb)
	
	def create_toolbar(self):
		for p in self.perspectives:
			p.create_toolbar()
		
		# create sys toolbars
		self.tb = tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
							 agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
		tb.SetToolBitmapSize(wx.Size(48, 48))
		tb.AddSimpleTool(wx.ID_ABOUT , _('About'), images.zhao32.GetBitmap(), short_help_string=_('About'))
		tb.Realize()
		# perspective.py alway show toolbar which start with sys_
		self._mgr.AddPane(tb, aui.AuiPaneInfo().Name('sys_tb1').Caption(_('System')).ToolbarPane().Top())

	def create_statusbar(self):
		self.statusbar = self.CreateStatusBar(2, wx.STB_SIZEGRIP)
		self.statusbar.SetStatusWidths([-2, -3])
		self.statusbar.SetStatusText("Ready", 0)

		for p in self.perspectives:
			p.create_status()

	def create_panes(self):
		# min size for the frame itself isn't completely done.
		# see the end up AuiManager.Update() for the test
		# code. For now, just hard code a frame minimum size
		self.SetMinSize(wx.Size(400, 300))

		for p in self.perspectives:
			p.create_panes()	

		perspective_default = self.perspectives[0].get_perspective()
		self._mgr.LoadPerspective(perspective_default)

		# "commit" all changes made to AuiManager
		self._mgr.Update()	

	def bind_events(self):
		for p in self.perspectives:
			p.bind_events()
		
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.Bind(wx.EVT_TOOL, self.on_about, id=wx.ID_ABOUT)

	def on_close(self, event):
		self._mgr.UnInit()
		event.Skip()

	def on_about(self, event):
		info = wx.adv.AboutDialogInfo()
		info.Name = _('PyToolset')
		info.Version = VER
		info.Copyright = '(c) 2017-2018 Zhao Wei'
		info.Description = _('A Python toolset of web crawler for personal use.')
		info.WebSite = ('https://github.com/yewberry/pytoolset', 'Github home page')
		info.Developers = ['Zhao Wei (yew1998@gmail.com)']
		wx.adv.AboutBox(info)

