"""
Test log utility
"""
import sys
sys.path.append('./pyproject')

import zw.logger as logger
logger.getLogger(__name__).debug('haha')
