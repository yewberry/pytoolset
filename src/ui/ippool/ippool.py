import wx
import wx.lib.agw.aui as aui
from blinker import signal

import zw.images as images
import zw.logger as logger

from ui.perspective import Perspective
from ui.ippool.ledpanel import LEDPanel
from ui.ippool.ipgrid import IPGrid
from ui.ippool.testgrid import TestGrid
import ui.ids as ids

LOG = logger.getLogger(__name__)
PANE_IDS = [
	'IPPOOL_TOOLBAR',
	'IPPOOL_LEDPANEL',
	'IPPOOL_IPLIST',
	'IPPOOL_TESTLIST',
	'IPPOOL_LOGWND'
]

SIG_LOG = signal('log')

class IPPoolPerspective(Perspective):
	def __init__(self, parent, mgr):
		Perspective.__init__(self, parent, mgr)
	
	def create_panes(self):
		self.led_panel = LEDPanel(self._par)
		self.ip_grid = IPGrid(self._par)
		self.tt_grid = TestGrid(self._par)
		self.log_wnd = wx.TextCtrl(self._par, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)

		# add a bunch of panes
		self._mgr.AddPane(self.led_panel, aui.AuiPaneInfo().Name(PANE_IDS[1]).CaptionVisible(False).
						BestSize(wx.Size(200,50)).MinSize(wx.Size(200,50)).
						Top().Fixed().CloseButton(True).MaximizeButton(True))

		self._mgr.AddPane(self.ip_grid, aui.AuiPaneInfo().Name(PANE_IDS[2]).CenterPane())
		self._mgr.AddPane(self.tt_grid, aui.AuiPaneInfo().Name(PANE_IDS[3]).Caption(_('Proxy testing')).
						BestSize(wx.Size(400,100)).MinSize(wx.Size(400,100)).
						Right().Position(0).CloseButton(False).MaximizeButton(True))

		
		self._mgr.AddPane(self.log_wnd, aui.AuiPaneInfo().Name(PANE_IDS[4]).Caption( _('Message') ).
						  Right().Position(1).CloseButton(False).MaximizeButton(True))
		
		SIG_LOG.connect(self.on_log)
	
	def create_menu(self):
		menu = wx.Menu()
		menu.Append(ids.ID_IPP_TOGGLE, _('Start IP Pool'))
		menu.Append(ids.ID_IPP_TEST_TOOGLE, _('Start IP Test'))
		menu.AppendSeparator()
		return [{'title': _('IP Pool'), 'menu': menu}]
	
	def create_toolbar(self):
		tb1 = aui.AuiToolBar(self._par, -1, wx.DefaultPosition, wx.DefaultSize,
							 agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
		tb1.SetToolBitmapSize(wx.Size(48, 48))
		tb1.AddSimpleTool(ids.ID_IPP_TEST_TOOGLE, "Test", images.zhao32.GetBitmap())
		tb1.AddSeparator()
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_WARNING))
		tb1.AddSimpleTool(wx.ID_ANY, "Test", wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE))
		tb1.Realize()
		self._mgr.AddPane(tb1, aui.AuiPaneInfo().Name(PANE_IDS[0]).Caption("Big Toolbar").ToolbarPane().Top())

	def bind_events(self):
		self._par.Bind(wx.EVT_TOOL, self.on_ip_test, id=ids.ID_IPP_TEST_TOOGLE)

	def setup_perspective(self):
		for p in PANE_IDS:
			self._mgr.GetPane(p).Show()
	
	def on_ip_test(self, evt):
		pass
		# self.tt_grid.start_worker()
	
	def on_log(self, dat):
		s = '%s\n' % dat
		wx.CallAfter(self.log_wnd.write, s)

