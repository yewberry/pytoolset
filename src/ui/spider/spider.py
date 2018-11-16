import os
import threading
import wx
import wx.aui as aui
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

			db = Database()
			for idx,el in enumerate(regions):
				#TODO 从亚洲开始
				if idx < 2:
					continue
				btn = el.find_element_by_tag_name('span')
				arr = el.find_elements_by_tag_name('a')
				region_name = arr[0].text.strip()
				drv.execute_script("arguments[0].scrollIntoView();", btn)
				time.sleep(3)
				drv.execute_script("arguments[0].onclick();", btn)
				# btn.click()
				self.wait_factiva_load()
				countries = el.find_elements_by_css_selector('div li')
				if len(countries)>0:
					first_item = countries[0].find_elements_by_tag_name('a')[0].text.strip()
					if region_name == '亚洲' or region_name == '非洲' or first_item == '太平洋岛国':
						LOG.info('%s含子区域!'%region_name)
						sub_regions = el.find_elements_by_css_selector('div li')
						for sub_idx,sub_reg in enumerate(sub_regions):
							#TODO 从亚洲的亚洲南部开始
							if sub_idx<3:
								continue
							subbtn = sub_reg.find_element_by_tag_name('span')
							subarr = sub_reg.find_elements_by_tag_name('a')
							subregion_name = subarr[0].text.strip()
							drv.execute_script("arguments[0].scrollIntoView();", subbtn)
							time.sleep(3)
							drv.execute_script("arguments[0].onclick();", subbtn)
							# subbtn.click()
							self.wait_factiva_load()
							sub_countries = sub_reg.find_elements_by_css_selector('div li')
							LOG.info('%s下，子区域%s 国家数:%s'%(region_name, subregion_name, len(sub_countries)))
							self.process_countries(drv, db, sub_countries, region_name, subregion_name)
					else:
						LOG.info('%s下国家数:%s'%(region_name, len(countries)))
						self.process_countries(drv, db, countries, region_name)
				else:
					LOG.info('%s无国家数据!'%region_name)

		finally:
			pass
			#drv.quit()
	def wait_factiva_load(self):
		try:
			WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'mnuMsg')))
			LOG.info('Found loading..')
			WebDriverWait(self.browser, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'mnuMsg')))
			LOG.info('Loading gone..')
		except Exception as e:
			LOG.info('Wait loading timeout')
		time.sleep(5)
	
	def find_popup_field_value(self, html_str, key):
		key_val = key.strip()
		soup = BeautifulSoup(html_str)
		trs = soup.find_all('tr')
		rtn = None
		for idx, tr in enumerate(trs):
			if idx < 2:
				continue
			if len(tr)<3:
				continue
			key_td = tr.contents[0]
			val_td = tr.contents[2]
			if key_td.text.strip() == key_val:
				rtn = val_td.div.text.strip() if val_td.div else val_td.text.strip()
				break
		return rtn
	
	def process_countries(self, drv, db, countries, region_name, sub_region=''):
		for cidx,country in enumerate(countries):
			recs = []
			cbtn = country.find_element_by_tag_name('span')
			carr = country.find_elements_by_tag_name('a')	
			country_name = carr[0].text.strip()
			if country_name == '大中华地区':
				drv.execute_script("arguments[0].scrollIntoView();", cbtn)
				time.sleep(3)
				drv.execute_script("arguments[0].onclick();", cbtn)
				self.wait_factiva_load()
				china_countries = country.find_elements_by_css_selector('div li')
				LOG.info('%s下，子地数:%s'%(country_name, len(china_countries)))
				self.process_countries(drv, db, china_countries, region_name, sub_region)
				continue
			drv.execute_script("arguments[0].scrollIntoView();", cbtn)
			time.sleep(3)
			drv.execute_script("arguments[0].onclick();", cbtn)
			# cbtn.click()
			self.wait_factiva_load()
			sources = country.find_elements_by_css_selector('div li')
			LOG.info('%s下数据源数:%s'%(country_name, len(sources)))
			for source_idx,source in enumerate(sources):
				sarr = source.find_elements_by_tag_name('a')
				process_source_name = sarr[0].text.replace('\n', '').split(':')[1].strip()
				LOG.info('%s/%s'%(source_idx+1, len(sources)))
				LOG.info('Process %s'%process_source_name)
				detail_btn = sarr[1]
				drv.execute_script("arguments[0].scrollIntoView();", detail_btn)
				popup_script = detail_btn.get_attribute('onclick')
				drv.execute_script(popup_script)
				try:
					WebDriverWait(drv, 30).until(EC.visibility_of_element_located((By.ID, '_ceprogress__overlay')))
					WebDriverWait(drv, 30).until(EC.invisibility_of_element_located((By.ID, '_ceprogress__overlay')))
				except Exception as e:
					pass
				time.sleep(3)
				popup = drv.find_element_by_class_name('popup-body')
				raw_text = drv.execute_script("return arguments[0].outerHTML;", popup)

				soup = BeautifulSoup(raw_text)
				trs = soup.find_all('tr')
				count = 0
				while len(trs)<1 and count<3:
					LOG.info('Not found popup, try again for %s'%process_source_name)
					action_chains = ActionChains(drv)
					action_chains.send_keys(Keys.ESCAPE).perform()
					drv.execute_script(popup_script)
					time.sleep(15)
					popup = drv.find_element_by_class_name('popup-body')
					raw_text = drv.execute_script("return arguments[0].outerHTML;", popup)
					soup = BeautifulSoup(raw_text)
					trs = soup.find_all('tr')
					count += 1
				if len(trs)<1:
					LOG.error('%s source %s not processed!'%(source_idx, process_source_name))
					continue
				name = trs[0].find('img').attrs['title'].strip()
				desc = self.find_popup_field_value(raw_text, '描述:')
				code = self.find_popup_field_value(raw_text, '资讯来源代码:')
				lang = self.find_popup_field_value(raw_text, '语言:')
				freq = self.find_popup_field_value(raw_text, '频数:')
				link = self.find_popup_field_value(raw_text, '网址:')

				o = {'uid': None, 'name':name, 'region':region_name, 'sub_region':sub_region, 'country':country_name
				, 'raw_text':raw_text, 'description':desc, 'source_code':code, 'language':lang
				, 'frequecy':freq, 'link':link}
				recs.append(o)
				LOG.info('Get info %s'%name)

				action_chains = ActionChains(drv)
				action_chains.send_keys(Keys.ESCAPE).perform()
			db.insert_update(recs
					, 'spider_factiva_region_check'
					, 'spider_factiva_region_insert'
					, 'spider_factiva_region_update'
					, ['region', 'country', 'name'])


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
		drv.set_window_size( 600, s.height )
		return drv

	def stop_browser(self):
		if self.browser is not None:
			self.browser.quit()
			del self.browser
			self.browser = None
	
	def _show_cur_center_pane(self):
		for p in self.panes:
			pane = self.mgr.GetPane(p)
			if pane.dock_direction == aui.AUI_DOCK_CENTER:
				pane.Show(p == self.cur_spider.name)




