import wx
from blinker import signal

from zw.database import Database
from ui.ledctrl import LEDCtrl
from ui.ippool.statpanel import StatPanel
from ui.ippool.taskpanel import TaskPanel

class PoolPanel(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition
				, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self.init_ui()
		self.load_data()
		self.bind_event()
	
	def init_ui(self):
		led_size = (100, 50)
		self.led_total = LEDCtrl(self, -1, size=led_size, fgcolor='white')
		self.led_succ = LEDCtrl(self, -1, size=led_size)
		self.led_fail = LEDCtrl(self, -1, size=led_size, fgcolor='yellow')
		bsizer1 = wx.BoxSizer(wx.HORIZONTAL)
		bsizer1.Add(self.led_total, 1, wx.ALIGN_CENTER)
		bsizer1.Add(self.led_succ, 1, wx.ALIGN_CENTER)
		bsizer1.Add(self.led_fail, 1, wx.ALIGN_CENTER)

		
		self.statpanel = statpanel = StatPanel(self)
		self.taskpanel = taskpanel = TaskPanel(self)
		self.logwindow = logwindow = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)

		bsizer3 = wx.BoxSizer(wx.VERTICAL)
		bsizer3.Add(taskpanel, 1, wx.EXPAND)
		bsizer3.Add(logwindow, 1, wx.EXPAND)
		bsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		bsizer2.Add(statpanel, 1, wx.EXPAND, border=10)
		bsizer2.Add(bsizer3, 1, wx.EXPAND, border=10)

		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(bsizer1, 0, wx.EXPAND)
		s.Add(bsizer2, 1, wx.EXPAND)
		self.SetSizer(s)

	def load_data(self):
		db = Database()
		rows = db.query('ippool_count')
		self.led_total.SetValue(str(rows[0].c))
	
	def bind_event(self):
		sig_refresh = signal('refresh')
		sig_refresh.connect(self.refresh)
		sig_crawl_start = signal('crawl_start')
		sig_crawl_start.connect(self.on_crawl_start)
		sig_crawl_result = signal('crawl_result')
		sig_crawl_result.connect(self.on_crawl_result)
		sig_crawl_block = signal('crawl_block')
		sig_crawl_block.connect(self.on_log)

		sig_task_start = signal('task_start')
		sig_task_start.connect(self.on_task_start)
		sig_task_succ = signal('task_succ')
		sig_task_succ.connect(self.on_task_succ)
		sig_task_fail = signal('task_fail')
		sig_task_fail.connect(self.on_task_fail)

	def refresh(self, sender):
		wx.CallAfter(self.load_data)

	def on_crawl_start(self, dat):
		d = [ '爬取:%s\n' % x for x in dat]
		wx.CallAfter(self.write_log, d)
	def on_crawl_result(self, dat):
		d = '插入:%s，更新:%s\n' % (dat[0], dat[1])
		wx.CallAfter(self.write_log, [d])
	def on_log(self, dat):
		d = '%s\n' % dat
		wx.CallAfter(self.write_log, [d])
	def on_task_start(self, dat):
		d = '通过代理:%s:%s, 连接类型:%s,访问www.baidu.com\n'%(dat[0], dat[1], dat[2])
		wx.CallAfter(self.write_log, [d])
	def write_log(self, dat):
		for d in dat:
			self.logwindow.write(d)
	
	def on_task_succ(self, dat):
		wx.CallAfter(self.update_led, self.led_succ, dat*1)
	def on_task_fail(self, dat):
		wx.CallAfter(self.update_led, self.led_fail, dat*-1)
	def update_led(self, led, num):
		v = int(led.GetValue())	+ num
		led.SetValue(str(v))	

		