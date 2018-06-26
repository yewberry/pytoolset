import random
import wx
import wx.dataview as dv
import zw.images as images

class StatPanel(wx.Panel):
	def __init__(self, parent, db):
		wx.Panel.__init__(self, parent, -1)
		self.db = db
		self.dvc = dvc = dv.DataViewCtrl(self,
								   style=wx.BORDER_THEME
								   | dv.DV_ROW_LINES # nice alternating bg colors
								   #| dv.DV_HORIZ_RULES
								   | dv.DV_VERT_RULES
								   | dv.DV_MULTIPLE
								   )

		# rows = [
		# 	{'ip': '127.0.0.1', 'port': '8080', 'country': 'cn', 'city': '江苏', 'speed': 80, 'update_time': '2018-06-26 20:48:17'},
		# 	{'ip': '127.0.0.2', 'port': '8080', 'country': 'cn', 'city': '江苏', 'speed': 80, 'update_time': '2018-06-26 20:48:17'},
		# 	{'ip': '127.0.0.3', 'port': '8080', 'country': 'cn', 'city': '江苏', 'speed': 80, 'update_time': '2018-06-26 20:48:17'},
		# ]
		rows = db.query('SELECT * FROM ippool')
		rows = rows.as_dict()
		rows = [ [d['country'],d['ip'],d['port'],d['city'],d['speed']] for d in rows]


		self.model = StatListModel(rows)
		# Tel the DVC to use the model
		dvc.AssociateModel(self.model)
		
		dvc.AppendIconTextColumn('国家', 0, width=30)
		dvc.AppendTextColumn("IP地址", 1, width=120)
		dvc.AppendTextColumn("端口", 2, width=50)
		dvc.AppendTextColumn('服务器地址', 3, width=100)
		dvc.AppendProgressColumn('速度', 4, width=100)
		dvc.SetIndent(0)
		for c in dvc.Columns:
			c.Sortable = True
			c.Reorderable = True
			c.MinWidth = 30
			# c.Alignment = wx.ALIGN_CENTER
			# c.Renderer.Alignment = wx.ALIGN_CENTER

		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(dvc, 1, wx.EXPAND)
	
	def onDeleteRows(self, evt):
		# Remove the selected row(s) from the model. The model will take care
		# of notifying the view (and any other observers) that the change has
		# happened.
		items = self.dvc.GetSelections()
		rows = [self.model.GetRow(item) for item in items]
		self.model.DeleteRows(rows)
		
	def onAddRow(self, evt):
		id = len(self.model.data) + 1
		value = ['cn', '127.0.0.1', '8080', '江苏', 80]
		self.model.AddRow(value)

class StatListModel(dv.DataViewIndexListModel):
	def __init__(self, data):
		dv.DataViewIndexListModel.__init__(self, len(data))
		self.data = data
		
	def GetColumnType(self, col):
		'''
		string bool datetime
		'''
		return 'string'

	def GetValueByRow(self, row, col):
		if col == 0:
			return wx.dataview.DataViewIconText(text="", icon=images.flag_cn.Icon)
		else:
			return self.data[row][col]
	
	def GetColumnCount(self):
		return len(self.data[0])
	
	def GetCount(self):
		return len(self.data)
		
	def GetAttrByRow(self, row, col, attr):
		if col == 3:
			attr.SetColour('blue')
			attr.SetBold(True)
			return True
		return False
		
	def SetValueByRow(self, value, row, col):
		'''
		readonly grid return true
		'''
		return True

	def Compare(self, item1, item2, col, ascending):
		if not ascending: # swap sort order?
			item2, item1 = item1, item2
		row1 = self.GetRow(item1)
		row2 = self.GetRow(item2)
		return self.data[row1][col] < self.data[row2][col]
	
	def DeleteRows(self, rows):
		# make a copy since we'll be sorting(mutating) the list
		rows = list(rows)
		# use reverse order so the indexes don't change as we remove items
		rows.sort(reverse=True)
		
		for row in rows:
			# remove it from our data structure
			del self.data[row]
			# notify the view(s) using this model that it has been removed
			self.RowDeleted(row)
			
	def AddRow(self, value):
		# update data structure
		self.data.append(value)
		# notify views
		self.RowAppended()

