from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

headers = ["Scientist name", "Birthdate", "Contribution"]


class TableModel(QAbstractTableModel):
    def __init__(self,parent=None):
        super(TableModel,self).__init__(parent
                                        )
        self.rows = [['zhangjie','19941116','哈哈哈']]

    def rowCount(self, parent):
        print(len(self.rows))
        return len(self.rows)
    def columnCount(self, parent):
        return len(headers)
    def data(self, index, role):
        print(index)
        if role != Qt.DisplayRole:
            return QVariant()
        return self.rows[index.row()][index.column()]
    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return QVariant()
        return headers[section]

    def  setData(self,index,value,role=Qt.EditRole):
        print('MyListModel setData', index.column(), index.row())
        # 如果当前为编辑角色
        if role == Qt.EditRole:
            # print("setData Qt.EditRole")
            # print(type(value))
            # print(value)
            # QVariant的这个方法，返回的bool类型表示这个值是否可以被转为int类型
            value_int = value
            row=index.row()
            col=index.column()
            # 保存数据
            self.rows[row][col] = value_int
            # 发射数据更改信号，以便让view更新
            self.dataChanged.emit(index, index)
            # 数据是否成功更新
            return True

    def flags(self, index):
        #首先获取超类的flags返回值
        flag=super(QAbstractTableModel,self).flags(index)
        #或运算，将ItemIsEditable（可编辑）标志叠加上去
        return flag | Qt.ItemIsEditable

    def rowsInserted(self, QModelIndex, p_int, p_int_1):
        self.rows.append(['a','b','c'])

app = QApplication([])
qmodel = TableModel()
view = QTableView()
view.editTriggers()
view.setModel(qmodel)
qmodel.rowsInserted(0,0,0)
qmodel.rowsInserted(0,0,0)
qmodel.rowsInserted(0,0,0)
view.update()
view.show()
app.exec_()