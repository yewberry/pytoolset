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
			#TODO 从非洲开始
			if ridx < 11:
				continue
			btn = region.find_element_by_tag_name('span')
			arr = region.find_elements_by_tag_name('a')
			region_name = arr[0].text.strip()
			self.scroll_and_click(btn)
			items = region.find_elements_by_css_selector('div li')
			for idx,item in enumerate(items):
				#TODO 从澳大利亚/大洋洲开始
				# if region_name == '澳大利亚/大洋洲' and idx < 2:
				# 	continue
				self.process_item(region_name, item)
	
	def crawling_cata_industry(self, drv, usr, pwd):
		self.drv = drv
		self.login(usr, pwd)
		self.load_search_page()
		drv.find_element_by_id('inTab').click()
		self.wait_loading()
		self.process_tree('div[id=inMnu] li', self.process_cata_industry)
		LOG.info('Complete!')
	
	def crawling_cata_expert(self, drv, usr, pwd):
		self.drv = drv
		self.login(usr, pwd)
		self.load_search_page()
		drv.find_element_by_id('fesTab').click()
		self.wait_loading()
		self.process_tree('div[id=fesMnu]>ul>li', self.process_cata_expert)
		LOG.info('Complete!')
	
	def crawling_cata_news(self, drv, usr, pwd):
		self.drv = drv
		self.login(usr, pwd)
		self.load_search_page()
		drv.find_element_by_id('nsTab').click()
		self.wait_loading()
		self.process_tree('div[id=nsMnu]>ul>li', self.process_cata_news)
		LOG.info('Complete!')
	
	def crawling_by_industry(self, drv, usr, pwd):
		self.drv = drv
		self.login(usr, pwd)
		self.load_search_page()
		drv.find_element_by_id('scTab').click()
		self.wait_loading()
		select = Select(drv.find_element_by_id('scCat'))
		select.select_by_visible_text('按行业')
		self.wait_loading()
		self.process_tree('div[id=scMnu]>ul>li', self.process_by_industry)
		LOG.info('Complete!')		
	
	def process_cata_industry(self, txt, el):
		# ex. 休闲/艺术/餐饮与酒店业_剧院/娱乐场所_博物馆/古迹/花园
		arr = txt.split('_')
		o = {'uid':None}
		idx = -1
		for idx,s in enumerate(arr):
			o['cata%s'%idx] = s
		for i in range(idx+1, 8):
			o['cata%s'%i] = ''
		self.db.insert([o], 'spider_factiva_cata_industry_insert')
		LOG.info('Insert:'+txt)
	
	def process_cata_expert(self, txt, el):
		arr = txt.split('_')
		o = {'uid':None}
		idx = -1
		for idx,s in enumerate(arr):
			o['cata%s'%idx] = s
		for i in range(idx+1, 8):
			o['cata%s'%i] = ''
		self.db.insert([o], 'spider_factiva_cata_expert_insert')
		LOG.info('Insert:'+txt)

	def process_cata_news(self, txt, el):
		arr = txt.split('_')
		o = {'uid':None}
		idx = -1
		for idx,s in enumerate(arr):
			o['cata%s'%idx] = s
		for i in range(idx+1, 8):
			o['cata%s'%i] = ''
		self.db.insert([o], 'spider_factiva_cata_news_insert')
		LOG.info('Insert:'+txt)

	def process_by_industry(self, txt, el):
		drv = self.drv
		arr = txt.split('_')
		o = {'uid':None}
		idx = -1
		for idx,s in enumerate(arr):
			o['cata%s'%idx] = s
		for i in range(idx+1, 8):
			o['cata%s'%i] = ''
		
		max_retry = 3
		count = 0
		sarr = el.find_elements_by_tag_name('a')
		process_source_name = sarr[0].text.replace('\n', '').split(':')[1].strip()
		detail_btn = sarr[1]
		LOG.info('Process %s'%process_source_name)
		while count<max_retry:
			count += 1
			popup = self.show_detail_dialog(detail_btn)
			if popup is None:
				LOG.error('Fail to popup dialog, try again!')
				continue
			raw_text = drv.execute_script("return arguments[0].outerHTML;", popup)
			soup = BeautifulSoup(raw_text)
			trs = soup.find_all('tr')
			if len(trs)<1:
				LOG.error('Popup dialog is empty, try again!')
				continue
			name = trs[0].find('img').attrs['title'].strip()
			link = self.find_popup_field_value(raw_text, '网址:')
			o['name'] = name
			o['raw_text'] = raw_text
			o['link'] = link
			break
			
		if count>=max_retry:
			LOG.error('%s source not processed!'%process_source_name)
			return
		
		self.db.insert([o], 'spider_factiva_by_industry_insert')
		LOG.info('Get info %s'%o['name'])

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
	
	def load_search_page(self):
		drv = self.drv
		rtn = False
		try:
			drv.get('https://global.factiva.com/sb/default.aspx?NAPC=S')
			LOG.info('Wait search page shown...')
			WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.ID, 'inpillscontextmenu')))
			LOG.info('Search page shown!')
			rtn = True
		except Exception as e:
			LOG.error('Search page not found!')
			traceback.print_exc()
		return rtn
	
	def process_tree(self, selector, cb=None):
		drv = self.drv
		top_items = drv.find_elements_by_css_selector(selector)
		LOG.info('Top-level items num:%s' % len(top_items))
		for idx,item in enumerate(top_items):
			self.process_tree_item( item, cb, idx_str='%s/%s' % (idx+1, len(top_items)) )
	
	def process_tree_item(self, el, cb=None, parent_str='', idx_str=''):
		if self.is_tree_leaf(el):
			LOG.info('Process leaf:%s'%idx_str)
			self.process_item_info(el, cb, parent_str)
		else:
			item_btn = el.find_element_by_class_name('mnuBtn')
			self.scroll_and_click(item_btn)
			sub_items = el.find_elements_by_xpath('./div/ul/li')
			for sidx,sub_item in enumerate(sub_items):
				etxt = self.get_tree_node_text(el)
				pstr = etxt if parent_str == '' else parent_str+'_'+etxt
				istr = '%s_%s/%s' % (idx_str, sidx+1, len(sub_items))
				self.process_tree_item(sub_item, cb, pstr, istr)
	
	def process_item_info(self, el, cb=None, parent_str=''):
		txt = parent_str+'_'+self.get_tree_node_text(el)
		if cb is None:
			LOG.info(item_text)
		else:
			cb(txt, el)
	
	def show_detail_dialog(self, detail_btn):
		drv = self.drv
		popup = None
		try:
			drv.execute_script("arguments[0].scrollIntoView();", detail_btn)
			action_chains = ActionChains(drv)
			action_chains.send_keys(Keys.ESCAPE).perform()
			popup_script = detail_btn.get_attribute('onclick')
			drv.execute_script(popup_script)
			WebDriverWait(drv, 3).until(EC.visibility_of_element_located((By.ID, 'relInfoPopupBalloon__overlay')))
			popup = drv.find_element_by_class_name('popup-body')
			time.sleep(2)
		except Exception as e:
			pass
		return popup

	def is_tree_leaf(self, el):
		b = None
		try:
			b = el.find_element_by_class_name('mnuBtn')
		except Exception as e:
			pass
		return True if b is None else False
	
	def get_tree_node_text(self, el):
		arr = el.find_elements_by_tag_name('a')
		txt = arr[0].text.strip()
		# txt = txt.replace(' ', '')
		return txt

	def wait_loading(self, wait=30):
		drv = self.drv
		wait_show = 3
		wait_hide = wait
		finish = False
		div = None
		for i in range(0, wait_show):
			time.sleep(1)
			LOG.info('Try find loading div...')
			try:
				div = drv.find_element_by_class_name('mnuMsg')
				txt = div.text
				if txt == '正在加载...':
					break
			except Exception as e:
				pass
		if div is not None:
			LOG.info('Start loading...')
			for i in range(0, wait_hide):
				time.sleep(1)
				try:
					div = drv.find_element_by_class_name('mnuMsg')
					txt = div.text
					if txt != '正在加载...':
						finish = True
						break
				except Exception as e:
					finish = True
					break
		else:
			LOG.info('Loading div not found, suppose finish loading')
			finish = True
		LOG.info('Finish loading.' if finish else 'Load timeout, suppose finished loading.')

	def scroll_and_click(self, el):
		drv = self.drv
		drv.execute_script("arguments[0].scrollIntoView();", el)
		time.sleep(1)
		drv.execute_script("arguments[0].onclick();", el)
		self.wait_loading()

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
################################################################################
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
				#TODO 英国
				# if region_name == '欧洲' and index == -1 and sidx < 16:
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

		# rows = self.db.query('spider_factiva_all')
		# for idx,r in enumerate(rows):
		# 	index = self.InsertItem(self.GetItemCount(), r.name)
		# 	self.SetItem(index, 1, r.region)
		# 	self.SetItem(index, 2, r.country)
		# 	self.SetItem(index, 3, r.description)
		# 	self.SetItem(index, 4, r.source_code)
		# 	self.SetItem(index, 5, r.language)
		# 	self.SetItem(index, 6, r.frequecy)
		# 	self.SetItem(index, 7, ''+r.link)
		# 	self.SetItemData(index, idx)

