import os
import wx
import zw.logger as logger
from zw.utils import Timeit
from ui.ribbonframe import RibbonFrame
LOG = logger.getLogger(__name__)
class App(wx.App):
	def OnInit(self):
		t = Timeit()
		LOG.debug("OnInit")

		frm = RibbonFrame(None, -1, '我的工具集合(yew1998@gmail.com)', size=(800, 600))
		frm.Show()

		LOG.debug('Elapsed time: %f ms' % t.end())
		return True

	def OnExit(self):
		# exit but main process still there why?
		wx.Exit()




