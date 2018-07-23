import wx
# -- wx.SizeReportCtrl --
# (a utility control that always reports it's client size)
class SizeReportCtrl(wx.Control):

	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, mgr=None):

		wx.Control.__init__(self, parent, id, pos, size, wx.NO_BORDER)
		self._par = parent
		self._mgr = mgr
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

	@staticmethod
	def create(par, mgr, width=80, height=80):
		ctrl = SizeReportCtrl(par, -1, wx.DefaultPosition, wx.Size(width, height), mgr)
		return ctrl

	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		size = self.GetClientSize()
		s = ("Size: %d x %d")%(size.x, size.y)

		dc.SetFont(wx.NORMAL_FONT)
		w, height = dc.GetTextExtent(s)
		height = height + 3
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.SetPen(wx.WHITE_PEN)
		dc.DrawRectangle(0, 0, size.x, size.y)
		dc.SetPen(wx.LIGHT_GREY_PEN)
		dc.DrawLine(0, 0, size.x, size.y)
		dc.DrawLine(0, size.y, size.x, 0)
		dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2))

		if self._mgr:
			pi = self._mgr.GetPane(self)
			s = ("Layer: %d")%pi.dock_layer
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*1))

			s = ("Dock: %d Row: %d")%(pi.dock_direction, pi.dock_row)
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*2))

			s = ("Position: %d")%pi.dock_pos
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*3))

			s = ("Proportion: %d")%pi.dock_proportion
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*4))

	def OnEraseBackground(self, event):
		# intentionally empty
		pass

	def OnSize(self, event):
		self.Refresh()
		event.Skip()