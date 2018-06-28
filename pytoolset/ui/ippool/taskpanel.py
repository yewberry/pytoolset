import time
import threading
from multiprocessing.dummy import Pool as ThreadPool
import wx
import wx.dataview as dv
import requests
from blinker import signal

import zw.images as images
from zw.database import Database
import zw.logger as logger

LOG = logger.getLogger(__name__)

sig_task_result = signal('task_result')
sig_task_succ = signal('task_succ')
sig_task_fail = signal('task_fail')
sig_task_start = signal('task_start')

class TaskPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		self.init_ui()
		self.load_data()
		self.bind_event()
		self.start_worker()

	def init_ui(self):
		self.dvc = dvc = dv.DataViewCtrl(self,
								   style=wx.BORDER_THEME
								   | dv.DV_ROW_LINES # nice alternating bg colors
								   #| dv.DV_HORIZ_RULES
								   | dv.DV_VERT_RULES
								   | dv.DV_MULTIPLE
								   )
		dvc.AppendTextColumn("待测IP", 0, width=120)
		dvc.AppendTextColumn("端口", 1, width=50)
		dvc.AppendTextColumn('连接类型', 2, width=100)
		dvc.AppendProgressColumn('测试结果', 3, width=100)
		dvc.SetIndent(0)
		for c in dvc.Columns:
			c.Sortable = True
			c.Reorderable = True
			c.MinWidth = 30
			# c.Alignment = wx.ALIGN_CENTER
			# c.Renderer.Alignment = wx.ALIGN_CENTER
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(dvc, 1, wx.EXPAND)

	def load_data(self):
		rows = self.getall()
		self.model = TaskListModel(rows)
		# Tel the DVC to use the model
		self.dvc.AssociateModel(self.model)
	
	def bind_event(self):
		sig_task_result.connect(self.on_task_result)

	def on_task_result(self, dat):
		wx.CallAfter(self.update_status, dat)

	def update_status(self, dat):
		self.model.update_row(dat)
		if dat['status_code'] == 200:
			sig_task_succ.send(1)
		else:
			sig_task_fail.send(1)

	def do_task(self, proxy):
		idx = proxy[len(proxy)-1]
		ip = proxy[0]
		port = proxy[1]
		conn_type = proxy[2]
		conn_type = conn_type.lower() if conn_type else 'http'
		if conn_type == 'http':
			proxies = {
				'http': 'http://%s:%s' % (ip, port)
			}
		else:
			proxies = {
				'https': 'http://%s:%s' % (ip, port)
			}
		sig_task_start.send(proxy)
		r = requests.get('http://www.baidu.com', proxies=proxies)
		sig_task_result.send({'idx':idx, 'status_code':r.status_code})

	def start_worker(self):		
		self.worker = TaskWorkerThread(self.model.data, self.do_task)
		self.worker.start()

	def stop_worker(self):
		self.worker.stop()

	def getall(self):
		db = Database()
		rows = db.query('ippool_all')
		rows = rows.as_dict()
		rows = [ [d['ip'], d['port'], d['conn_type'], 0] for d in rows]
		return rows

class TaskListModel(dv.DataViewIndexListModel):
	def __init__(self, data):
		dv.DataViewIndexListModel.__init__(self, len(data))
		self.data = data
		
	def GetColumnType(self, col):
		'''
		string bool datetime
		'''
		return 'string'

	def GetValueByRow(self, row, col):
		return self.data[row][col]
	
	def GetColumnCount(self):
		return len(self.data[0])
	
	def GetCount(self):
		return len(self.data)
		
	def GetAttrByRow(self, row, col, attr):
		if col == 3:
			attr.SetColour('blue')
			attr.SetBold(True)
			return True
		return False
		
	def SetValueByRow(self, value, row, col):
		'''
		readonly grid return true
		'''
		return True

	def Compare(self, item1, item2, col, ascending):
		if not ascending: # swap sort order?
			item2, item1 = item1, item2
		row1 = self.GetRow(item1)
		row2 = self.GetRow(item2)
		return self.data[row1][col] < self.data[row2][col]

	def update_row(self, dat):
		idx = dat['idx']
		code = dat['status_code']
		if code == 200:
			self.data[idx][3] = 100
		else:
			self.data[idx][3] = 0
		self.RowChanged(idx)

class TaskWorkerThread(threading.Thread):
	def __init__(self, dat, proc_func, interval=3, pool_size=8):
		super(TaskWorkerThread, self).__init__()
		self.dat = dat
		self.proc_func = proc_func
		self.interval = interval
		self.pool_size = pool_size
		self.thread_stop = False

	def run(self):
		self.thread_stop = False
		LOG.debug('Start task thread')
		step = 5
		proxys = []
		for idx, proxy in enumerate(self.dat):
			if self.thread_stop:
				break
			proxy.append(idx)
			proxys.append(proxy)
			if idx % step == 0:
				pool = ThreadPool(self.pool_size)
				results = pool.map(self.proc_func, proxys)
				# close the pool and wait for the work to finish
				pool.close()
				pool.join()
				proxys[:] = []
				time.sleep(self.interval)
		LOG.debug('Finish task thread')

	def stop(self):
		self.thread_stop = True