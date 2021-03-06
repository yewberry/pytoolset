import os
import wx

import zw.logger as logger
from zw.utils import Timeit
from zw.config import Config
from zw.database import Database

# set _ function in builtins for i18n
import builtins
builtins.__dict__['_'] = wx.GetTranslation

LOG = logger.getLogger(__name__)
class App(wx.App):
	cfg_path = property(lambda s: s._cfg_path, lambda s, v: setattr(s, '_cfg_path', v))
	cfg = property(lambda s: s._cfg, lambda s, v: setattr(s, '_cfg', v))

	def OnInit(self):
		t = Timeit()
		LOG.info("OnInit")

		# load locale from cur dir in locale
		# TODO mac, place locale in app
		locale = wx.Locale(wx.LANGUAGE_CHINESE_SIMPLIFIED)
		if locale.IsOk():
			locale.AddCatalogLookupPathPrefix('locale')
			locale.AddCatalog('app')

		self.cfg_path = 'cfg.json'
		# init config file
		self.cfg = Config(self.cfg_path, {
			'version': '1.0.0',
			'database': {
				'dbtype': 'sqlite',
				'dbname': 'data.db',
				'dbuser': '',
				'dbpass': '',
				'dbaddr': 'localhost',
			},
			'ippool': {
				'urls': ['http://www.xicidaili.com/nn/'],
				'interval': 60,
			}
		}).data
		# init db
		Database(self.cfg['database']).init_db()

		# from ui.ribbonframe import RibbonFrame
		# frm = RibbonFrame(None, -1, '爬虫工具集 v0.1 yew1998@gmail.com', size=(1024, 768))
		# frm.Show()
		from ui.auiframe import AuiFrame
		frm = AuiFrame(None, -1, _('Personal Python Tools'), size=(1024, 768))
		frm.Show()
		
		LOG.info('Elapsed time: %f ms' % t.end())
		return True

	def OnExit(self):
		# TODO exit but main process still there why?
		wx.Exit()




