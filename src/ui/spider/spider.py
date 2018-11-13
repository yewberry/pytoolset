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
from ui.spider.factiva import FactivaSpider
from ui.spider.zhihu import ZhihuSpider
from ui.spider.weibo import WeiboSpider

LOG = logger.getLogger(__name__)

class SpiderPerspective(Perspective):
	def __init__(self, parent, mgr):
		Perspective.__init__(self, parent, mgr)
		self.factiva = FactivaSpider(parent)
		self.zhihu = ZhihuSpider(parent)
		self.weibo = WeiboSpider(parent)
		self.hm = {
			ids.ID_SPIDER_FACTIVA: 'center_factiva',
			ids.ID_SPIDER_ZHIHU: 'center_zhihu',
			ids.ID_SPIDER_WEIBO: 'center_weibo'
		}
	
	def create_panes(self):
		# self.browser_panel = wx.Panel(self.parent, style=wx.WANTS_CHARS, size=(500, 300))
		self.log_wnd = wx.TextCtrl(self.parent, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(200, 300))

		# add a bunch of panes
		# SizeReportCtrl.create(self.parent, self.mgr)
		self.add_pane(self.factiva.get_center_pane(), aui.AuiPaneInfo().Name(self.hm[ids.ID_SPIDER_FACTIVA]).CenterPane())
		self.add_pane(self.zhihu.get_center_pane(), aui.AuiPaneInfo().Name(self.hm[ids.ID_SPIDER_ZHIHU]).CenterPane())
		self.add_pane(self.weibo.get_center_pane(), aui.AuiPaneInfo().Name(self.hm[ids.ID_SPIDER_WEIBO]).CenterPane())
		self.add_pane(self.log_wnd, aui.AuiPaneInfo().Bottom().Caption(_('Message') )
					.CloseButton(False).MaximizeButton(True))
	
	def create_menu(self):
		menu = wx.Menu()
		menu.Append(ids.ID_SPIDER_FACTIVA, _('Factiva'))
		menu.AppendSeparator()	
		return [{'title': _('Spider'), 'menu': menu}]
	
	def create_toolbar(self):
		tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
		tb.SetToolBitmapSize(wx.Size(32, 32))
		tb.AddTool(ids.ID_SPIDER_FACTIVA, _('Factiva'), images.factiva.GetBitmap(), shortHelp=_('Start Factiva spider'))
		tb.AddTool(ids.ID_SPIDER_ZHIHU, _('Zhihu'), images.zhihu.GetBitmap(), shortHelp=_('Start Zhihu spider'))
		tb.AddTool(ids.ID_SPIDER_WEIBO, _('Weibo'), images.weibo.GetBitmap(), shortHelp=_('Start Weibo spider'))
		tb.AddSeparator()
		tb.Realize()
		self.add_pane(tb, aui.AuiPaneInfo().Caption(_('Toolbar')).ToolbarPane()
					.Top().LeftDockable(False).RightDockable(False))

	def setup_perspective(self):
		for p in self.panes:
			if not p.startswith('center_') or p == self.hm[ids.ID_SPIDER_FACTIVA]:
				self.mgr.GetPane(p).Show()

	def bind_events(self):
		wx.App.Get().Bind(logger.EVT_WX_LOG_EVENT, self.on_log)
		self.parent.Bind(wx.EVT_TOOL, self.on_spider_show)
		#self.parent.Bind(wx.EVT_TOOL, self.on_factiva, id=ids.ID_SPIDER_FACTIVA)
	
	def on_log(self, dat):
		wx.CallAfter(self.log_wnd.write, '%s\n' % dat.msg)
	
	def on_spider_show(self, evt):
		pane_nm = self.hm[evt.GetId()]
		for p in self.panes:
			if p.startswith('center_'):
				print(p == pane_nm)
				self.mgr.GetPane(p).Show(p == pane_nm)
		self.mgr.Update()
	
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
		# browser.get('https://cn.bing.com')
	
	def on_close(self):
		if hasattr(self, 'browser'):
			self.browser.quit()

	def on_factiva(self, evt):
		pass
		#self.browser.get('https://snapshot.factiva.com/Pages/Index')



