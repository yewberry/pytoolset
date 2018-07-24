import wx
from blinker import signal

from zw.database import Database
from ui.ledctrl import LEDCtrl

SIG_REFRESH = signal('refresh')

class LEDPanel(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition
				, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		wx.Panel.__init__(self, parent, id, pos, size, style)

		led_size = (100, 50)
		self.led_total = LEDCtrl(self, size=led_size, fgcolor='white')
		self.led_succ = LEDCtrl(self, size=led_size, fgcolor='green')
		self.led_fail = LEDCtrl(self, size=led_size, fgcolor='red')
		
		bsizer = wx.BoxSizer(wx.HORIZONTAL)
		bsizer.Add(self.led_total, 1, wx.ALIGN_CENTER)
		bsizer.Add(self.led_succ, 1, wx.ALIGN_CENTER)
		bsizer.Add(self.led_fail, 1, wx.ALIGN_CENTER)

		self.SetSizer(bsizer)
		self.load_data()
		self.bind_events()

	def load_data(self):
		db = Database()
		r = db.query('ippool_count')[0]
		c = r.c if r.c is not None else 0
		s = r.s if r.s is not None else 0
		f = r.f if r.f is not None else 0
		self.led_total.set_value(c)
		self.led_succ.set_value(s)
		self.led_fail.set_value(f)
	
	def bind_events(self):
		SIG_REFRESH.connect(self.refresh)
	
	def refresh(self, sender):
		wx.CallAfter(self.load_data)