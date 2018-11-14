from abc import ABCMeta, abstractmethod
import wx

class Perspective:
	__metaclass__: ABCMeta
	def __init__(self, parent, mgr):
		'''
		:param mgr: aui.AuiManager object
		'''
		self.parent = parent
		self.mgr = mgr
		self.panes = []

	@abstractmethod
	def create_panes(self):
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
	
	def post_init(self):
		pass
	
	def get_perspective(self):
		self.hide_all_panes()
		self.setup_perspective()
		perspective = self.mgr.SavePerspective()
		return perspective

	def setup_perspective(self):
		for p in self.panes:
			self.mgr.GetPane(p).Show()

	def hide_all_panes(self):
		all_panes = self.mgr.GetAllPanes()
		for i in range(len(all_panes)):
			pane = all_panes[i]
			if not pane.IsToolbar():
				pane.Hide()
			elif not pane.name.startswith('sys_'):
				pane.Hide()
	
	def add_pane(self, ctrl, opts):
		nm = opts.name if opts.name else '%s_%d' % ('pane',wx.NewId())
		opts.Name(nm)
		self.mgr.AddPane(ctrl, opts)
		self.panes.append(nm)

	def on_close(self):
		pass
