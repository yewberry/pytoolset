import os
import wx
import wx.lib.mixins.listctrl as listmix
import traceback

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

LOG = logger.getLogger(__name__)

class FactivaSpider:
	name = property(lambda s: s._name, lambda s, v: setattr(s, '_name', v))
	def __init__(self, parent, name):
		self.parent = parent
		self.name = name
		self.list = None
		self.drv = None
		self.db = None

	def get_center_pane(self):
		if self.list is None:
			self.db = Database()
			self.list = FactivaListCtrl(self.parent, self.db, style=wx.LC_REPORT | wx.BORDER_NONE)
		return self.list
	
	def crawling(self, drv, usr, pwd):
		self.drv = drv
		self.login(usr, pwd)
		regions = self.get_regions()
		if regions is None:
			regions = self.get_regions()

		for ridx,region in enumerate(regions):
			#TODO 从欧洲开始
			if ridx < 8:
				continue
			btn = region.find_element_by_tag_name('span')
			arr = region.find_elements_by_tag_name('a')
			region_name = arr[0].text.strip()
			self.scroll_and_click(btn)
			items = region.find_elements_by_css_selector('div li')
			for idx,item in enumerate(items):
				#TODO 从美国开始
				# if region_name == '南美洲' and idx < 6:
				# 	continue
				self.process_item(region_name, item)
	
	def login(self, usr, pwd):
		drv = self.drv
		drv.get('https://global.factiva.com/factivalogin/login.asp?productname=global')
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
		except Exception as e:
			traceback.print_exc()
	
	def get_regions(self):
		drv = self.drv
		regions = None
		try:
			drv.get('https://global.factiva.com/sb/default.aspx?NAPC=S')
			LOG.info('Wait search page show...')
			WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.ID, 'inpillscontextmenu')))
			LOG.info('Search page complete.')
			drv.find_element_by_id('scTab').click()
			select = Select(drv.find_element_by_id('scCat'))
			LOG.info('Wait 按地区 show...')
			select.select_by_visible_text('按地区')
			self.wait_load()

			LOG.info('按地区 complete.')
			regions = drv.find_elements_by_css_selector('div[id=scMnu] li')
			LOG.info('地区数:%s'%len(regions))
		except Exception as e:
			traceback.print_exc()
		return regions
	
	def process_item(self, region_name, el, index=-1, count=0):
		if self.is_leaf(el):
			self.process_source(region_name, el, index, count)
		else:
			item_btn = el.find_element_by_tag_name('span')
			self.scroll_and_click(item_btn)
			sub_items = el.find_elements_by_css_selector('div li')
			for sidx,sub_item in enumerate(sub_items):
				#TODO 马利兰
				# if region_name == '北美洲' and index == -1 and sidx < 49:
				# 	continue
				self.process_item(region_name, sub_item, sidx, len(sub_items))

	def process_source(self, region_name, source, index, count):
		LOG.info('%s %s/%s'%(region_name, index+1, count))
		drv = self.drv
		sarr = source.find_elements_by_tag_name('a')
		process_source_name = sarr[0].text.replace('\n', '').split(':')[1].strip()
		LOG.info('Process %s'%process_source_name)

		count = 0
		popup = None
		detail_btn = sarr[1]
		drv.execute_script("arguments[0].scrollIntoView();", detail_btn)
		popup_script = detail_btn.get_attribute('onclick')
		drv.execute_script(popup_script)
		try:
			# time.sleep(5)
			WebDriverWait(drv, 3).until(EC.visibility_of_element_located((By.ID, '_ceprogress__overlay')))
			WebDriverWait(drv, 3).until(EC.invisibility_of_element_located((By.ID, '_ceprogress__overlay')))
			popup = drv.find_element_by_class_name('popup-body')
		except Exception as e:
			pass
		time.sleep(3)
		while popup is None and count<3:
			LOG.info('Not found popup, try again for %s'%process_source_name)
			action_chains = ActionChains(drv)
			action_chains.send_keys(Keys.ESCAPE).perform()
			drv.execute_script(popup_script)
			time.sleep(15)
			popup = drv.find_element_by_class_name('popup-body')
		if popup is None:
			LOG.error('%s source %s not processed!'%process_source_name)
			return			
		
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
			return

		db = self.db
		recs = []
		country_name = source.find_element_by_xpath('./../../..').find_elements_by_tag_name('a')[0].text.strip()
		sub_region = source.find_element_by_xpath('./../../../../../..').find_elements_by_tag_name('a')[0].text.strip()
		district = None
		if sub_region == '美国':
			district = country_name
			country_name = sub_region
			sub_region = region_name
		name = trs[0].find('img').attrs['title'].strip()
		desc = self.find_popup_field_value(raw_text, '描述:')
		code = self.find_popup_field_value(raw_text, '资讯来源代码:')
		lang = self.find_popup_field_value(raw_text, '语言:')
		freq = self.find_popup_field_value(raw_text, '频数:')
		link = self.find_popup_field_value(raw_text, '网址:')

		o = {'uid': None, 'name':name, 'region':region_name, 'sub_region':sub_region, 'country':country_name
		, 'district':district if district is not None else '', 'raw_text':raw_text, 'description':desc, 'source_code':code, 'language':lang
		, 'frequecy':freq, 'link':link}
		recs.append(o)

		action_chains = ActionChains(drv)
		action_chains.send_keys(Keys.ESCAPE).perform()

		db.insert_update(recs
				, 'spider_factiva_region_check'
				, 'spider_factiva_region_insert'
				, 'spider_factiva_region_update'
				, ['region', 'sub_region', 'country', 'district', 'name'])
		LOG.info('Get info %s'%name)
	
	def scroll_and_click(self, el):
		drv = self.drv
		drv.execute_script("arguments[0].scrollIntoView();", el)
		time.sleep(1)
		drv.execute_script("arguments[0].onclick();", el)
		self.wait_load()

	def wait_load(self):
		try:
			WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'mnuMsg')))
			LOG.info('Found loading..')
			WebDriverWait(self.browser, 20).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'mnuMsg')))
			LOG.info('Loading gone..')
		except Exception as e:
			LOG.info('Wait loading timeout')
		time.sleep(10)
	
	def is_leaf(self, el):
		b = None
		try:
			b = el.find_element_by_class_name('mnuBtn')
		except Exception as e:
			pass		
		return True if b is None else False

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

class FactivaListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, db, ID=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		self.db = db
		self.InsertColumn(0, _('name'))
		self.InsertColumn(1, _('region'))
		self.InsertColumn(2, _('country'))
		self.InsertColumn(3, _('description'))
		self.InsertColumn(4, _('source code'))
		self.InsertColumn(5, _('language'))
		self.InsertColumn(6, _('frequecy'))
		self.InsertColumn(7, _('link'))

		rows = self.db.query('spider_factiva_all')
		for idx,r in enumerate(rows):
			index = self.InsertItem(self.GetItemCount(), r.name)
			self.SetItem(index, 1, r.region)
			self.SetItem(index, 2, r.country)
			self.SetItem(index, 3, r.description)
			self.SetItem(index, 4, r.source_code)
			self.SetItem(index, 5, r.language)
			self.SetItem(index, 6, r.frequecy)
			self.SetItem(index, 7, ''+r.link)
			self.SetItemData(index, idx)

