import os
import multiprocessing
import threading
import time
import requests
import wx
from blinker import signal

SIG_UPDATE = signal('update')

def main():
	app = wx.App()
	frm = MyFrame(None, title='multiprocess')
	frm.Show()
	app.MainLoop()

class MyFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title)
		self.tc = tc = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
		SIG_UPDATE.connect(self.update)

		if False:
			self.do_multiprocess()
		
		if True:
			sub_thread = SubThread()
			sub_thread.start()

	def do_multiprocess(self):
		dat = range(100)
		pool = multiprocessing.Pool()
		for r in pool.map_async(worker, dat).get():
			self.tc.write('%s %s\n' % (time.time(), r))
		pool.close()
		pool.join()

	def update(self, txt):
		wx.CallAfter(self.append_text, txt)
	def append_text(self, txt):
		self.tc.write('%s %s\n' % (time.time(), txt))

class SubThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		dat = range(30)
		cores = multiprocessing.cpu_count()
		pool = multiprocessing.Pool(processes=cores)
		
		for p in dat:
			rs = pool.apply_async( worker, (p,))
			rs = rs.get()
			SIG_UPDATE.send(str(rs))

		pool.close()
		pool.join()
		SIG_UPDATE.send('thread end')

# must def worker func in top level, otherwise you will get 'can't pickle objects' error
def worker(o):
	rtn = None
	session = requests.Session()
	session.trust_env = False # Don't read proxy settings from OS
	try:
		r = session.get('http://www.baidu.com', timeout=5)
		rtn = True if r.status_code == 200 else False
	except:
		rtn = False
	# time.sleep(1)
	print('%s %s' % (time.time(), str(os.getpid())))
	return 'Process %s return' % str(os.getpid())

if __name__ == '__main__':
	main()