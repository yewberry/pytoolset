from abc import ABCMeta, abstractmethod

class Perspective:
	__metaclass__: ABCMeta
	def __init__(self, parent, mgr):
		'''
		:param mgr: aui.AuiManager object
		'''
		self._par = parent
		self._mgr = mgr

	@abstractmethod
	def create_panes(self):
		pass

	@abstractmethod
	def setup_perspective(self):
		pass
	
	def create_menu(self):
		'''
		:return:[ {title:string, menu: wx.Menu} ] 
		'''
		pass

	def create_toolbar(self):
		pass
	
	def create_status(self):
		pass
	
	def bind_events(self):
		pass
	
	def get_perspective(self):
		self.hide_all_panes()
		self.setup_perspective()
		perspective = self._mgr.SavePerspective()
		return perspective

	def hide_all_panes(self):
		all_panes = self._mgr.GetAllPanes()
		for i in range(len(all_panes)):
			pane = all_panes[i]
			if not pane.IsToolbar():
				pane.Hide()
			elif not pane.name.startswith('sys_'):
				pane.Hide()