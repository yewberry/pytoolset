import wx
import wx.aui as aui

import wx.adv
from version import VER

import zw.images as images
import zw.logger as logger
import zw.utils as utils

import ui.ids as ids
# from ui.ippool.ippool import IPPoolPerspective
from ui.sizereportctrl import SizeReportCtrl
from ui.spider.spider import SpiderPerspective

LOG = logger.getLogger(__name__)

class AuiFrame(wx.Frame):

	def __init__(self, parent, id=wx.ID_ANY, title="", pos= wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE|wx.SUNKEN_BORDER, log=None):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)

		self.mgr = aui.AuiManager()
		# tell AuiManager to manage this frame
		self.mgr.SetManagedWindow(self)
		self.mgr.SetFlags(self.mgr.GetFlags() ^ aui.AUI_MGR_ALLOW_ACTIVE_PANE)
		self.perspectives = []
		# self.perspectives.append(IPPoolPerspective(self, self.mgr))
		self.perspectives.append(SpiderPerspective(self, self.mgr))
		self.tb = None

		self.create_menubar()
		self.create_toolbar()
		self.create_statusbar()
		self.create_panes()
		self.bind_events()
		self.SetIcon(images.zhao.GetIcon())
		LOG.debug('MainFrame actual size: %s' % self.GetSize())

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
		file_menu.Append(ids.ID_SWITCH_PANE, _("S&witch Window...") + "\t" + switcherAccel)
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
		# create sys toolbars
		self.tb = tb = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize
								, wx.TB_FLAT | wx.TB_NODIVIDER)
		tb.SetToolBitmapSize(wx.Size(32, 32))
		tb.AddTool(wx.ID_ABOUT , _('About'), images.help.GetBitmap(), shortHelp=_('About'))
		tb.Realize()
		# perspective.py alway show toolbar which start with sys_
		self.mgr.AddPane(tb, aui.AuiPaneInfo().Name('sys_tb1').Caption(_('System')).ToolbarPane().Top())

		for p in self.perspectives:
			p.create_toolbar()

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
		
		if len(self.perspectives) > 0:
			perspective_default = self.perspectives[0].get_perspective()
			self.mgr.LoadPerspective(perspective_default)

		# "commit" all changes made to AuiManager
		self.mgr.Update()	

	def bind_events(self):
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.Bind(wx.EVT_TOOL, self.on_about, id=wx.ID_ABOUT)

		for p in self.perspectives:
			p.bind_events()

	def on_close(self, evt):
		self.mgr.UnInit()
		for p in self.perspectives:
			p.on_close()
		evt.Skip()

	def on_about(self, evt):
		info = wx.adv.AboutDialogInfo()
		info.Name = _('PyToolset')
		info.Version = VER
		info.Copyright = '(c) 2017-2018 Zhao Wei'
		info.Description = _('A Python toolset for personal use.')
		info.WebSite = ('https://github.com/yewberry/pytoolset', 'Github home page')
		info.Developers = ['Zhao Wei (yew1998@gmail.com)']
		wx.adv.AboutBox(info)
