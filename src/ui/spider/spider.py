import os
import threading
import wx
import wx.aui as aui
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

import zw.images as images
import zw.logger as logger
import zw.utils as utils
from zw.database import Database

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
		self.factiva = FactivaSpider(parent, 'spider_factiva')
		self.zhihu = ZhihuSpider(parent, 'spider_zhihu')
		self.weibo = WeiboSpider(parent, 'spider_weibo')
		self.cur_spider = self.factiva

		self.toolbar = None
		self.browser = None
		self.cfg = wx.GetApp().cfg
	
	def create_panes(self):
		# self.browser_panel = wx.Panel(self.parent, style=wx.WANTS_CHARS, size=(500, 300))
		self.log_wnd = wx.TextCtrl(self.parent, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(200, 300))

		# add a bunch of panes
		# SizeReportCtrl.create(self.parent, self.mgr)
		self.add_pane(self.factiva.get_center_pane(), aui.AuiPaneInfo().Name(self.factiva.name).CenterPane())
		self.add_pane(self.zhihu.get_center_pane(), aui.AuiPaneInfo().Name(self.zhihu.name).CenterPane())
		self.add_pane(self.weibo.get_center_pane(), aui.AuiPaneInfo().Name(self.weibo.name).CenterPane())
		self.add_pane(self.log_wnd, aui.AuiPaneInfo().Bottom().Caption(_('Message') )
					.CloseButton(False).MaximizeButton(True))
	
	def create_menu(self):
		menu = wx.Menu()
		menu.Append(ids.ID_SPIDER_FACTIVA, _('Factiva'))
		menu.AppendSeparator()	
		return [{'title': _('Spider'), 'menu': menu}]
	
	def create_toolbar(self):
		self.toolbar = tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
		tb.SetToolBitmapSize(wx.Size(32, 32))
		tb.AddTool(ids.ID_SPIDER_FACTIVA, _('Factiva'), images.factiva.GetBitmap(), bmpDisabled=wx.NullBitmap
				, shortHelp=_('Start Factiva spider'), clientData=self.factiva)
		tb.AddTool(ids.ID_SPIDER_ZHIHU, _('Zhihu'), images.zhihu.GetBitmap(), bmpDisabled=wx.NullBitmap
				, shortHelp=_('Start Zhihu spider'), clientData=self.zhihu)
		tb.AddTool(ids.ID_SPIDER_WEIBO, _('Weibo'), images.weibo.GetBitmap(), bmpDisabled=wx.NullBitmap
				, shortHelp=_('Start Weibo spider'), clientData=self.weibo)
		tb.AddSeparator()
		tb.AddTool(ids.ID_SPIDER_START, _('Start'), images.start.GetBitmap(), shortHelp=_('Start spider'))
		tb.AddTool(ids.ID_SPIDER_PAUSE, _('Pause'), images.pause.GetBitmap(), shortHelp=_('Pause spider'))
		tb.AddTool(ids.ID_SPIDER_STOP, _('Stop'), images.stop.GetBitmap(), shortHelp=_('Stop spider'))
		tb.EnableTool(ids.ID_SPIDER_START, True)
		tb.EnableTool(ids.ID_SPIDER_PAUSE, False)
		tb.EnableTool(ids.ID_SPIDER_STOP, False)
		tb.Realize()
		self.add_pane(tb, aui.AuiPaneInfo().Caption(_('Toolbar')).ToolbarPane()
					.Top().LeftDockable(False).RightDockable(False))

	def setup_perspective(self):
		self._show_cur_center_pane()
		for p in self.panes:
			pane = self.mgr.GetPane(p)
			if pane.dock_direction != aui.AUI_DOCK_CENTER:
				pane.Show()

	def bind_events(self):
		wx.App.Get().Bind(logger.EVT_WX_LOG_EVENT, self.on_log)
		self.parent.Bind(wx.EVT_TOOL, self.on_tool_click)
		#self.parent.Bind(wx.EVT_TOOL, self.on_factiva, id=ids.ID_SPIDER_FACTIVA)

	def on_close(self):
		self.stop_browser()
	
	def on_log(self, dat):
		wx.CallAfter(self.log_wnd.write, '%s\n' % dat.msg)
	
	def on_tool_click(self, evt):
		tool_id = evt.GetId()
		hm = {
			ids.ID_SPIDER_START: self.start_spider,
			ids.ID_SPIDER_PAUSE: self.pause_spider,
			ids.ID_SPIDER_STOP: self.stop_spider
		}
		if tool_id not in hm:
			spider = self.toolbar.GetToolClientData(tool_id)
			if spider.name != self.cur_spider.name:
				self.cur_spider = spider
				self._show_cur_center_pane()
				self.mgr.Update()
		else:
			hm[tool_id]()
	
	def _show_cur_center_pane(self):
		for p in self.panes:
			pane = self.mgr.GetPane(p)
			if pane.dock_direction == aui.AUI_DOCK_CENTER:
				pane.Show(p == self.cur_spider.name)
	
	def start_spider(self):
		self.toolbar.EnableTool(ids.ID_SPIDER_START, False)
		self.toolbar.EnableTool(ids.ID_SPIDER_PAUSE, True)
		self.toolbar.EnableTool(ids.ID_SPIDER_STOP, True)
		t = threading.Thread(target=self.start_factiva)
		t.start()

	def pause_spider(self):
		self.toolbar.EnableTool(ids.ID_SPIDER_START, True)
		self.toolbar.EnableTool(ids.ID_SPIDER_PAUSE, False)
		self.toolbar.EnableTool(ids.ID_SPIDER_STOP, True)

	def stop_spider(self):
		self.stop_browser()
		self.toolbar.EnableTool(ids.ID_SPIDER_START, True)
		self.toolbar.EnableTool(ids.ID_SPIDER_PAUSE, False)
		self.toolbar.EnableTool(ids.ID_SPIDER_STOP, False)

	def start_factiva(self):
		db = Database()
		obj = self.cfg['factiva']
		usr = obj['usr']
		pwd = obj['pwd']
		drv = self.init_browser()
		self.browser.get('https://global.factiva.com/factivalogin/login.asp?productname=global')
		try:
			LOG.info('Wait login page show...')
			WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.ID, 'darktooltip-undefined')))
			LOG.info('Login page show complete.')
			el_usr = drv.find_element_by_id('email')
			el_pwd = drv.find_element_by_id('password')
			el_btn = drv.find_element_by_class_name('sign-in')
			drv.execute_script("arguments[0].value = '%s';"%usr, el_usr)
			drv.execute_script("arguments[0].value = '%s';"%pwd, el_pwd)
			el_btn.click()
			LOG.info('Wait main page show...')
			WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.ID, 'dj_new-header')))
			LOG.info('Main page header complete.')
			search = drv.find_element_by_css_selector('a[title=搜索]')
			search.click()
			LOG.info('Wait search page show...')
			WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.ID, 'inpillscontextmenu')))
			LOG.info('Search page complete.')
			drv.find_element_by_id('scTab').click()
			select = Select(drv.find_element_by_id('scCat'))
			LOG.info('Wait 按地区 show...')
			select.select_by_visible_text('按地区')
			self.wait_factiva_load()

			LOG.info('按地区 complete.')
			regions = drv.find_elements_by_css_selector('div[id=scMnu] li')
			LOG.info('地区数:%s'%len(regions))
			for el in regions:
				btn = el.find_element_by_tag_name('span')
				arr = el.find_elements_by_tag_name('a')
				region_name = arr[0].text
				drv.execute_script("arguments[0].scrollIntoView();", btn)
				btn.click()
				self.wait_factiva_load()
				countries = el.find_elements_by_css_selector('div li')
				LOG.info('%s下国家数:%s'%(region_name, len(countries)))
				for country in countries:
					cbtn = country.find_element_by_tag_name('span')
					carr = country.find_elements_by_tag_name('a')	
					country_name = carr[0].text
					drv.execute_script("arguments[0].scrollIntoView();", cbtn)
					cbtn.click()
					self.wait_factiva_load()
					sources = country.find_elements_by_css_selector('div li')
					LOG.info('%s下数据源数:%s'%(country_name, len(sources)))
					for source in sources:
						sarr = source.find_elements_by_tag_name('a')	
						source_name = sarr[0].text
						detail_btn = sarr[1]
						drv.execute_script("arguments[0].scrollIntoView();", detail_btn)
						detail_btn.click()
						time.sleep(3)
						WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'popup-body')))
						popup = drv.find_element_by_class_name('popup-body')
						raw_text = drv.execute_script("return arguments[0].outerHTML;", popup)
						popup.find_element_by_class_name('overlayclose').click()

						soup = BeautifulSoup(raw_text)
						ctn = soup.find_all('table')[0]
						trs = ctn.find_all('tr')


		finally:
			pass
			#drv.quit()
	def wait_factiva_load(self):
		WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'mnuMsg')))
		WebDriverWait(self.browser, 30).until_not(EC.presence_of_element_located((By.CLASS_NAME, 'mnuMsg')))
		time.sleep(3)

	def init_browser(self):
		if self.browser is not None:
			return self.browser
		sw, _ = wx.DisplaySize()
		s = self.parent.GetSize()
		p = self.parent.GetPosition()
		drv_path = './bin/chromedriver'
		if utils.isWin32():
			drv_path = './bin/chromedriver.exe'
		self.browser = drv = webdriver.Chrome(executable_path=drv_path)
		drv.set_window_position(p.x + s.width, p.y)
		drv.set_window_size( (sw-s.width)/2, s.height )
		return drv

	def stop_browser(self):
		if self.browser is not None:
			self.browser.quit()
			del self.browser
			self.browser = None




