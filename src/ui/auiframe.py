import wx
import wx.lib.agw.aui as aui
from wx.lib.agw.aui import aui_switcherdialog as ASD
from ui.ippool.ippool import IPPoolPerspective
from ui.sizereportctrl import SizeReportCtrl

import zw.images as images
import zw.logger as logger
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
		# set frame icon
		self.SetIcon(images.zhao.GetIcon())

		self.ippool = IPPoolPerspective(self, self._mgr)

		self.create_menubar()
		self.create_toolbar()
		self.create_statusbar()
		self.create_panes()
		self.bind_events()

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
		file_menu.Append(wx.ID_EXIT, "Exit")

		ippool_menu = wx.Menu()
		ippool_menu.Append(ID_IPPOOL_START, "Create Text Control")
		ippool_menu.Append(ID_IPPOOL_VALID, "Create HTML Control")
		ippool_menu.AppendSeparator()

		mb.Append(file_menu, "File")
		mb.Append(ippool_menu, "IP Pool")

		self.SetMenuBar(mb)
	
	def create_toolbar(self):
		# prepare a few custom overflow elements for the toolbars' overflow buttons
		prepend_items, append_items = [], []
		item = aui.AuiToolBarItem()

		item.SetKind(wx.ITEM_SEPARATOR)
		append_items.append(item)

		item = aui.AuiToolBarItem()
		item.SetKind(wx.ITEM_NORMAL)
		item.SetId(ID_CUST_TOOLBAR)
		item.SetLabel("Customize...")
		append_items.append(item)

		# create some toolbars
		tb1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
							 agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
		tb1.SetToolBitmapSize(wx.Size(48, 48))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_ERROR))
		tb1.AddSeparator()
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_WARNING))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_HELP))
		tb1.SetCustomOverflowItems(prepend_items, append_items)
		tb1.Realize()

		# add the toolbars to the manager
		self._mgr.AddPane(tb1, aui.AuiPaneInfo().Name("sys_tb1").Caption("Big Toolbar").ToolbarPane().Top())

		self.ippool.create_toolbar()

	def create_statusbar(self):
		self.statusbar = self.CreateStatusBar(2, wx.STB_SIZEGRIP)
		self.statusbar.SetStatusWidths([-2, -3])
		self.statusbar.SetStatusText("Ready", 0)
		self.statusbar.SetStatusText("Welcome To wxPython!", 1)	

	def create_panes(self):
		# min size for the frame itself isn't completely done.
		# see the end up AuiManager.Update() for the test
		# code. For now, just hard code a frame minimum size
		self.SetMinSize(wx.Size(400, 300))
		
		self.ippool.create_panes()		

		perspective_default = self.ippool.get_perspective()
		self._mgr.LoadPerspective(perspective_default)

		# "commit" all changes made to AuiManager
		self._mgr.Update()	

	def bind_events(self):
		pass

	def __del__(self):
		pass


	def OnClose(self, event):
		self._mgr.UnInit()
		event.Skip()


