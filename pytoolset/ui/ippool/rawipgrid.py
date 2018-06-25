import wx.dataview as dv

class RawIpGrid(dv.DataViewListCtrl):
	def __init__(self, parent):
		dv.DataViewListCtrl.__init__(self, parent)

		self.AppendProgressColumn('id', width=100)
		self.AppendTextColumn('artist', width=170)
		self.AppendTextColumn('title', width=260)
		self.AppendIconTextColumn('genre', width=80)