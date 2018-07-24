import wx
import wx.lib.gizmos as gizmos

class LEDCtrl(gizmos.LEDNumberCtrl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize
				, style=gizmos.LED_ALIGN_CENTER|gizmos.LED_DRAW_FADED, value=0, fgcolor='green', bgcolor='black'):
		gizmos.LEDNumberCtrl.__init__(self, parent, id, pos, size, style)
		self.SetForegroundColour(fgcolor)
		self.SetBackgroundColour(bgcolor)
		self.SetValue(str(value))
	
	def set_value(self, val):
		self.SetValue(str(val))
	
	def add_value(self, val):
		val = int(self.GetValue()) + val
		self.SetValue(str(val))

