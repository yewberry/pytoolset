import os
import wx
import wx.aui as aui
from selenium import webdriver

import zw.images as images
import zw.logger as logger
import zw.utils as utils

from ui.perspective import Perspective
import ui.ids as ids

from ui.sizereportctrl import SizeReportCtrl

LOG = logger.getLogger(__name__)

class SpiderPerspective(Perspective):
	def __init__(self, parent, mgr):
		Perspective.__init__(self, parent, mgr)
	
	def create_panes(self):
		# self.browser_panel = wx.Panel(self.parent, style=wx.WANTS_CHARS, size=(500, 300))
		self.log_wnd = wx.TextCtrl(self.parent, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(200, 300))

		# add a bunch of panes
		self.add_pane(SizeReportCtrl.create(self.parent, self.mgr), aui.AuiPaneInfo().Name('Center').CenterPane())
		self.add_pane(self.log_wnd, aui.AuiPaneInfo().Bottom().Caption(_('Message') )
					.CloseButton(False).MaximizeButton(True))
		self.show_browser()
	
	def create_menu(self):
		menu = wx.Menu()
		menu.Append(ids.ID_SPR_TOGGLE, _('Start Spider'))
		menu.AppendSeparator()	
		return [{'title': _('Spider'), 'menu': menu}]
	
	def create_toolbar(self):
		tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
		tb.SetToolBitmapSize(wx.Size(32, 32))
		tb.AddTool(ids.ID_SPR_TOGGLE, _('Start'), images.zhao.GetBitmap())
		tb.AddSeparator()
		tb.Realize()
		self.add_pane(tb, aui.AuiPaneInfo().Caption(_('Toolbar')).ToolbarPane()
					.Top().LeftDockable(False).RightDockable(False))

	def bind_events(self):
		wx.App.Get().Bind(logger.EVT_WX_LOG_EVENT, self.on_log)
		self.parent.Bind(wx.EVT_TOOL, self.on_test, id=ids.ID_SPR_TOGGLE)
	
	def on_log(self, dat):
		wx.CallAfter(self.log_wnd.write, '%s\n' % dat.msg)
	
	def show_browser(self):
		sw, _ = wx.DisplaySize()
		s = self.parent.GetSize()
		p = self.parent.GetPosition()
		drv_path = './bin/chromedriver'
		if utils.isWin32():
			drv_path = './bin/chromedriver.exe'
		self.browser = browser = webdriver.Chrome(executable_path=drv_path)
		browser.set_window_position(p.x + s.width, p.y)
		browser.set_window_size( (sw-s.width)/2, s.height )
		browser.get('https://cn.bing.com')
	
	def on_close(self):
		self.browser.quit()



