import multiprocessing
import requests

def worker(idx):
	rtn = None
	session = requests.Session()
	session.trust_env = False # Don't read proxy settings from OS
	try:
		r = session.get('http://www.baidu.com', timeout=5)
		rtn = True if r.status_code == 200 else False
	except:
		rtn = False
	return 'Process %s return %s' % (idx,rtn)
 
def do_test():
	dat = range(100)
	pool = multiprocessing.Pool()
	for r in pool.map_async(worker, dat).get():
		print(r)
	pool.close()
	pool.join()

if __name__ == '__main__':
	do_test()