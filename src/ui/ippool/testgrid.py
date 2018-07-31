import time
import multiprocessing
import threading
import wx
import wx.dataview as dv
import requests
from blinker import signal

from zw.database import Database
import zw.logger as logger

LOG = logger.getLogger(__name__)
SIG_TASK_RESULT = signal('task_result')
SIG_REFRESH = signal('refresh')

class TestGrid(dv.DataViewCtrl):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, 
						style=wx.BORDER_THEME
						| dv.DV_ROW_LINES # nice alternating bg colors
						#| dv.DV_HORIZ_RULES
						| dv.DV_VERT_RULES
						| dv.DV_MULTIPLE)
		
		self.AppendTextColumn(_('IP'), 1, width=120)
		self.AppendTextColumn(_('Port'), 2, width=50)
		self.AppendTextColumn(_('Type'), 3, width=100)
		self.AppendProgressColumn(_('Result'), 4, width=100)
		self.SetIndent(0)
		for c in self.Columns:
			c.Sortable = True
			c.Reorderable = True
			c.MinWidth = 30
			# c.Alignment = wx.ALIGN_CENTER
			# c.Renderer.Alignment = wx.ALIGN_CENTER
		
		self.AssociateModel(TestGridModel.instance())
		#SIG_TASK_RESULT.connect(self.on_task_result)
		self.start_worker()

	def on_task_result(self, rec):
		wx.CallAfter(self.refresh_status, rec)
	def refresh_status(self, rec):
		self.GetModel().update(rec)

	def start_worker(self):
		model = self.GetModel()
		self.worker = WorkerThread(model.data)
		self.worker.start()

	def stop_worker(self):
		self.worker.stop()

class TestGridModel(dv.DataViewIndexListModel):
	def __init__(self, data):
		dv.DataViewIndexListModel.__init__(self, len(data))
		self.data = data
		self.cols = ['id', 'ip', 'port', 'conn_type', 'valid']
	
	@classmethod
	def instance(cls):
		db = Database()
		rows = db.query('ippool_all')
		rows = rows.as_dict()
		db.close()
		return TestGridModel(rows)

	def update(self, rec):
		for i,p in enumerate(self.data):
			if p['id'] == rec['id']:
				db = Database()
				db.query('ippool_update_valid', id=rec['id'], valid=rec['valid'])
				db.close()
				self.data[i] = rec
				self.RowChanged(i)
				break

	def GetColumnType(self, col):
		'''
		string bool datetime
		'''
		return 'string'

	def GetValueByRow(self, row, col):
		col_name = self.cols[col]
		return self.data[row][col_name]
	
	def GetColumnCount(self):
		return len(self.cols)
	
	def GetCount(self):
		return len(self.data)
		
	def GetAttrByRow(self, row, col, attr):
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
		row1 = self.data[row1]
		row2 = self.data[row2]
		label = self.cols[col]
		return row1[label] < row2[label]

def worker(o):
	rtn = o
	ip = rtn['ip']
	port = rtn['port']
	conn_type = rtn['conn_type'].lower()
	proxies = {'http': 'http://%s:%s' % (ip, port)} if conn_type == 'http' else\
				{'https': 'http://%s:%s' % (ip, port)}
	
	session = requests.Session()
	session.trust_env = False # Don't read proxy settings from OS

	try:
		r = session.get('http://www.baidu.com', timeout=5)
		rtn['valid'] = 100 if r.status_code == 200 else 0
	except:
		rtn['valid'] = 0
	print(rtn)
	return rtn

class WorkerThread(threading.Thread):
	def __init__(self, data, interval=5, step=5):
		super(WorkerThread, self).__init__()
		self.dat = data
		self.interval = interval
		self.step = step
		self.thread_stop = False

	def run(self):
		self.thread_stop = False
		LOG.debug('Start task thread in %s processes' % multiprocessing.cpu_count())
		proxys = []
		for idx, p in enumerate(self.dat):
			if self.thread_stop:
				break
			proxys.append(p)
			if idx % self.step == 0:
				pool = multiprocessing.Pool()
				for r in pool.map_async(worker, proxys).get():
					a = 0
					#SIG_TASK_RESULT.send(r)
				pool.close()
				pool.join()

				proxys[:] = []
				#SIG_REFRESH.send(self)
				time.sleep(self.interval)
		LOG.debug('Finish task thread')

	def stop(self):
		self.thread_stop = True
