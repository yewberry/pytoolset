import logging
import logging.config
from pathlib import Path

LOG_DIR = Path.home().joinpath('logs')
LOG_FILE = 'app.log'

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
				'maxBytes': 10485760,
				'backupCount': 20,
				'encoding': 'utf8',
				'level': logging.DEBUG,
			}
		},
		'loggers': {
			'': {
				'handlers': ['console', 'logfile'],
				'level': logging.DEBUG,
				'propagate': True
			}
		}
	})
	return logger
