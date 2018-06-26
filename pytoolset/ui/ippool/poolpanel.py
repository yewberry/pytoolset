import wx
import wx.lib.gizmos as gizmos
import records
import os.path

from ui.ippool.statpanel import StatPanel
from ui.ippool.taskpanel import TaskPanel

class PoolPanel(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition
				, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self._initDb('yew.db')
		self._initUi()
	
	def _initUi(self):
		bsizer1 = wx.BoxSizer(wx.HORIZONTAL)
		led_style = gizmos.LED_ALIGN_CENTER|gizmos.LED_DRAW_FADED
		led_size = (100, 50)

		self.led_total = gizmos.LEDNumberCtrl(self, -1, size=led_size, style=led_style)
		self.led_total.SetValue('0')
		self.led_total.SetForegroundColour('white')
		bsizer1.Add(self.led_total, 1, wx.ALIGN_CENTER)

		self.led_succ = gizmos.LEDNumberCtrl(self, -1, size=led_size, style=led_style)
		self.led_succ.SetValue('0')
		bsizer1.Add(self.led_succ, 1, wx.ALIGN_CENTER)

		self.led_fail = gizmos.LEDNumberCtrl(self, -1, size=led_size, style=led_style)
		self.led_fail.SetValue('0')
		self.led_fail.SetForegroundColour('yellow')
		bsizer1.Add(self.led_fail, 1, wx.ALIGN_CENTER)

		bsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.statpanel = statpanel = StatPanel(self, self.db)
		self.taskpanel = taskpanel = TaskPanel(self, self.db)
		bsizer2.Add(statpanel, 1, wx.EXPAND, border=10)
		bsizer2.Add(taskpanel, 1, wx.EXPAND, border=10)

		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(bsizer1, 0, wx.EXPAND)
		s.Add(bsizer2, 1, wx.EXPAND)
		self.SetSizer(s)

	def _initDb(self, db_path):
		# Valid SQLite URL forms are:
		#   sqlite:///:memory: (or, sqlite://)
		#   sqlite:///relative/path/to/file.db
		#   sqlite:////absolute/path/to/file.db
		if not os.path.isfile(db_path):
			self.db = db = records.Database('sqlite:///%s' % db_path)
			db.query("CREATE TABLE ippool (ip int PRIMARY KEY, port text, country text, city text, speed int, "
					+ "update_time TimeStamp NOT NULL DEFAULT (datetime('now','localtime')) )")
		else:
			self.db = records.Database('sqlite:///%s' % db_path)