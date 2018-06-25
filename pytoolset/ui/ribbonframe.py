import wx
import wx.ribbon as RB
import wx.lib.gizmos as gizmos
import wx.dataview as dv

import zw.images as images
import zw.utils as utils
import ui.trayicon as trayicon

ID_IP_POOL= wx.ID_HIGHEST + 1
ID_IP_TRACE = ID_IP_POOL + 1
ID_DN_TRACE = ID_IP_POOL + 2

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

		other_page = RB.RibbonPage(self._ribbon, wx.ID_ANY, '其他')
		self._ribbon.Realize()
		
		#--------------------------------------------------------------
		bsizer1 = wx.BoxSizer(wx.HORIZONTAL)
		led_style = gizmos.LED_ALIGN_CENTER|gizmos.LED_DRAW_FADED
		led_size = (100, 50)

		self.led_total = gizmos.LEDNumberCtrl(self._panel, -1, size=led_size, style=led_style)
		self.led_total.SetValue('0')
		self.led_total.SetForegroundColour('white')
		bsizer1.Add(self.led_total, 1, wx.ALIGN_CENTER)

		self.led_succ = gizmos.LEDNumberCtrl(self._panel, -1, size=led_size, style=led_style)
		self.led_succ.SetValue('0')
		bsizer1.Add(self.led_succ, 1, wx.ALIGN_CENTER)

		self.led_fail = gizmos.LEDNumberCtrl(self._panel, -1, size=led_size, style=led_style)
		self.led_fail.SetValue('0')
		self.led_fail.SetForegroundColour('yellow')
		bsizer1.Add(self.led_fail, 1, wx.ALIGN_CENTER)

		#--------------------------------------------------------------
		bsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		box1 = wx.StaticBox(self._panel, -1, 'IP爬取')
		box2 = wx.StaticBox(self._panel, -1, 'IP验证')

		self.dvRawIps = dvRawIps = dv.DataViewListCtrl(box1)
		self.dvCookedIps = dvCookedIps = dv.DataViewListCtrl(box2)
		bs = wx.BoxSizer()
		bs.Add(dvRawIps, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
		box1.SetSizer(bs)
		bs = wx.BoxSizer()
		bs.Add(dvCookedIps, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT)
		box2.SetSizer(bs)
		
		dvRawIps.AppendProgressColumn('id', width=100)
		dvRawIps.AppendTextColumn('artist', width=170)
		dvRawIps.AppendTextColumn('title', width=260)
		dvRawIps.AppendTextColumn('genre', width=80)

		dvCookedIps.AppendProgressColumn('id', width=100)
		dvCookedIps.AppendTextColumn('artist', width=170)
		dvCookedIps.AppendTextColumn('title', width=260)
		dvCookedIps.AppendTextColumn('genre', width=80)

		musicdata = [
			[10, "Bad English", "The Price Of Love", "Rock"],
			[20, "DNA featuring Suzanne Vega", "Tom's Diner", "Rock"],
			[30, "George Michael", "Praying For Time", "Rock"],
			[40, "Gloria Estefan", "Here We Are", "Rock"],
			[50, "Linda Ronstadt", "Don't Know Much", "Rock"],
			[60, "Michael Bolton", "How Am I Supposed To Live Without You", "Blues"]
		]
		
		for itemvalues in musicdata:
			print(itemvalues)
			dvRawIps.AppendItem(itemvalues)

		bsizer2.Add(box1, 1, wx.EXPAND)
		bsizer2.Add(box2, 1, wx.EXPAND)

		#--------------------------------------------------------------
		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(self._ribbon, 0, wx.EXPAND)
		s.Add(bsizer1, 0, wx.EXPAND)
		s.Add(bsizer2, 1, wx.EXPAND)
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
		
		if utils.isWin32():
			self.Bind(wx.EVT_ICONIZE, self.onIconify)
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def setArtProvider(self, prov):
		self._ribbon.DismissExpandedPanel()
		self._ribbon.Freeze()
		self._ribbon.SetArtProvider(prov)
		self._ribbon.Thaw()
		self._ribbon.Realize()

	def onToogleClick(self, event):
		tool_id = event.GetId()
		print( 'tool:{0}, state:{1}'.format( tool_id, event.IsChecked()) )
	
	def OnExtButton(self, event):
		wx.MessageBox('Extended button activated')

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

