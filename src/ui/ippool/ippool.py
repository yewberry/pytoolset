import wx
import wx.lib.agw.aui as aui
from ui.sizereportctrl import SizeReportCtrl
from ui.perspective import Perspective

import zw.images as images
import zw.logger as logger
LOG = logger.getLogger(__name__)

class IPPoolPerspective(Perspective):
	def __init__(self, parent, mgr):
		Perspective.__init__(self, parent, mgr)
		self._tb = None
	
	def create_panes(self):
		# add a bunch of panes
		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test1").Caption("Layer0 Top").Top().
						  CloseButton(True).MaximizeButton(True))

		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test2").Caption("Layer0 Bottom POS0").
						  Bottom().Position(0).CloseButton(True).MaximizeButton(True))
		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test3").Caption("Layer0 Bottom POS1").
						  Bottom().Position(1).CloseButton(True).MaximizeButton(True))

		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test4").Caption("Layer0 Left").
						  Left().CloseButton(True).MaximizeButton(True))

		# pos get row0
		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test5").Caption("Layer0 Right POS0").
						  Right().Position(0).CloseButton(True).MaximizeButton(True))
		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test6").Caption("Layer0 Right POS1").
						  Right().Position(1).CloseButton(True).MaximizeButton(True))
		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test7").Caption("Layer0 Right ROW1").
						  Right().Row(1).CloseButton(True).MaximizeButton(True))
		self._mgr.AddPane(SizeReportCtrl.create(self._par, self._mgr), aui.AuiPaneInfo().
						  Name("test8").Caption("Layer0 Right ROW2").
						  Right().Row(2).CloseButton(True).MaximizeButton(True))
	
	def create_toolbar(self):
		tb1 = aui.AuiToolBar(self._par, -1, wx.DefaultPosition, wx.DefaultSize,
							 agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
		tb1.SetToolBitmapSize(wx.Size(48, 48))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", images.zhao32.GetBitmap())
		tb1.AddSeparator()
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_WARNING))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE))
		tb1.Realize()
		self._mgr.AddPane(tb1, aui.AuiPaneInfo().Name("tb1").Caption("Big Toolbar").ToolbarPane().Top())
		self._tb = tb1

	def setup_perspective(self):
		self._tb.Show()
		self._mgr.GetPane("test1").Show()
		self._mgr.GetPane("test2").Show()
		self._mgr.GetPane("test3").Show()
		self._mgr.GetPane("test4").Show()

