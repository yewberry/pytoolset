import os
import wx
import wx.lib.mixins.listctrl as listmix

from selenium import webdriver

import zw.images as images
import zw.logger as logger
import zw.utils as utils

LOG = logger.getLogger(__name__)

class FactivaSpider:
	name = property(lambda s: s._name, lambda s, v: setattr(s, '_name', v))
	def __init__(self, parent, name):
		self.parent = parent
		self.name = name
		self.list = None

	def get_center_pane(self):
		if self.list is None:
			self.list = FactivaListCtrl(self.parent, 
									style=wx.LC_REPORT
									| wx.BORDER_NONE)
			self.list.InsertColumn(0, _('name'))
			self.list.InsertColumn(1, _('region'))
			self.list.InsertColumn(2, _('country'))
			self.list.InsertColumn(3, _('description'))
			self.list.InsertColumn(4, _('source code'))
			self.list.InsertColumn(5, _('language'))
			self.list.InsertColumn(6, _('frequecy'))
			self.list.InsertColumn(7, _('link'))
		return self.list

class FactivaListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)


