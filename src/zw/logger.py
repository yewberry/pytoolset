import logging
import logging.config
from pathlib import Path
import zw.utils as utils

EVT_WX_LOG_EVENT = None
WxLogEvent = None
try:
	import wx
	import wx.lib.newevent
	WxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()

except Exception as e:
	EVT_WX_LOG_EVENT = None
	WxLogEvent = None

LOG_DIR = 'logs'
if utils.isMacOS():
	LOG_DIR = Path.home().joinpath('logs')
LOG_FILE = 'app.log'

class MyEventHandler(logging.Handler):
	def __init__(self):
		logging.Handler.__init__(self)

	def emit(self, record):
		msg = self.format(record)
		if EVT_WX_LOG_EVENT is not None:
			evt = WxLogEvent(msg=msg)
			wx.PostEvent(wx.App.Get(), evt)

def getLogger(name=__name__):
	'''Get logger with name'''
	Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
	logger = logging.getLogger(name)
	logging.config.dictConfig({
		'version': 1,
		'disable_existing_loggers': False,  # this fixes the problem
		'formatters': {
			'simple': {
				'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
			},
			'short':{
				'format': '%(asctime)s %(message)s'
			},
		},
		'handlers': {
			'console': {
				'class': 'logging.StreamHandler',
				'formatter': 'simple',
				'level': logging.DEBUG,
			},
			'logfile': {
				'class': 'logging.handlers.RotatingFileHandler',
				'formatter': 'simple',
				'filename': Path(LOG_DIR).joinpath(LOG_FILE),
				'maxBytes': 10485760, # 10M
				'backupCount': 20,
				'encoding': 'utf8',
				'level': logging.DEBUG,
			},
			'eventmsg': {
				'class': 'zw.logger.MyEventHandler',
				'formatter': 'short',
				'level': logging.DEBUG,
			}
		},
		'loggers': {
			'': {
				'handlers': ['console', 'logfile', 'eventmsg'],
				'level': logging.DEBUG,
				'propagate': True
			}
		}
	})
	return logger
