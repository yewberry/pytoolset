import wx
import wx.ribbon as RB
import wx.dataview as dv

import zw.images as images
import zw.utils as utils
import ui.trayicon as trayicon
from ui.ippool.poolpanel import PoolPanel

ID_IP_POOL= wx.ID_HIGHEST + 1
ID_IP_TRACE = ID_IP_POOL + 1
ID_DN_TRACE = ID_IP_POOL + 2
ID_DN_TEST = ID_IP_POOL + 2

class RibbonFrame(wx.Frame):
	def __init__(self, parent, id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)

		#--------------------------------------------------------------
		self.toggles_ids= [ID_IP_POOL, ID_IP_TRACE, ID_DN_TRACE]
		if utils.isWin32():
			self._tbIcon = trayicon.TrayIcon(self, images.logo24.Icon)
		self._panel = wx.Panel(self)
		self._ribbon = RB.RibbonBar(self._panel, style=RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)

		rb_page = RB.RibbonPage(self._ribbon, wx.ID_ANY, 'IP与域名')

		ip_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, 'IP工具', style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE | RB.RIBBON_PANEL_EXT_BUTTON)
		ip_bar = RB.RibbonButtonBar(ip_panel, wx.ID_ANY)
		ip_bar.AddToggleButton(ID_IP_POOL, '代理IP池', images.IPPool.Bitmap)
		ip_bar.AddToggleButton(ID_IP_TRACE, 'IP跟踪', images.IPRadar.Bitmap)

		dns_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, '域名工具')
		dns_bar = RB.RibbonButtonBar(dns_panel, wx.ID_ANY)
		dns_bar.AddToggleButton(ID_DN_TRACE, '域名跟踪', images.domain.Bitmap)

		dns_bar.AddButton(ID_DN_TEST, "NormalButton", images.logo48.Bitmap)

		other_page = RB.RibbonPage(self._ribbon, wx.ID_ANY, '其他')
		self._ribbon.Realize()

		#--------------------------------------------------------------
		self.poolpanel = PoolPanel(self._panel, wx.ID_ANY)

		#--------------------------------------------------------------

		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(self._ribbon, 0, wx.EXPAND)
		s.Add(self.poolpanel, 1, wx.EXPAND)
		self._panel.SetSizer(s)

		self.BindEvents([ip_bar, dns_bar])
		#self.SetIcon(images.logo.Icon)
		self.CenterOnScreen()
		self.setArtProvider(RB.RibbonMSWArtProvider())

	def BindEvents(self, bars):
		bar0, bar1 = bars
		# toggle toolbar click
		for btn_id in self.toggles_ids:
			self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onToogleClick, id=btn_id)
		
		#self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.poolpanel.statpanel.onDeleteRows, id=btn_id)
		if utils.isWin32():
			self.Bind(wx.EVT_ICONIZE, self.onIconify)
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onToogleClick(self, event):
		tool_id = event.GetId()
		print( 'tool:{0}, state:{1}'.format( tool_id, event.IsChecked()) )

	def onIconify(self, event):
		self.Hide()

	def onClose(self, event):
		'''
		Destroy the taskbar icon and the frame
		'''
		if utils.isWin32():
			self._tbIcon.RemoveIcon()
			self._tbIcon.Destroy()
		self.Destroy()

	def setArtProvider(self, prov):
		self._ribbon.DismissExpandedPanel()
		self._ribbon.Freeze()
		self._ribbon.SetArtProvider(prov)
		self._ribbon.Thaw()
		self._ribbon.Realize()