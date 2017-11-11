import sys,select

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from PyQt4 import QtGui
from PyQt4 import QtCore


import serial,time




class myOutputText(QtGui.QWidget):
	def __init__(self,parent=None):
		super(myOutputText, self).__init__(parent)
		
		MainLayout = QtGui.QVBoxLayout()
		self.logOutput = QtGui.QTextEdit(parent)
		self.logOutput.setReadOnly(True)
		self.logOutput.setLineWrapMode(QtGui.QTextEdit.NoWrap)

		self.font = self.logOutput.font()
		self.font.setFamily("Courier")
		self.font.setPointSize(7)

		MainLayout.addWidget(self.logOutput)
		
		self.setLayout(MainLayout)
		self.lastState=''
	def addStuff(self,text):
		text=QtCore.QString(str(text)+'\n')
		
		if self.lastState!=text:
			self.logOutput.moveCursor(QtGui.QTextCursor.End)
			self.logOutput.setCurrentFont(self.font)
			#self.logOutput.setTextColor(color)


		
			self.logOutput.insertPlainText(text)
			self.lastState=text
			sb = self.logOutput.verticalScrollBar()
			sb.setValue(sb.maximum())
	def SerialRecive(self,info):
		info=str(info[1])
		#self.pixItemB.setPixmap(self.pixmapB)
		striped=''
		state=None
		#try:
		if '<TP>' in info:
			
			striped='>'+info.split('<TP>')[-1].split('</TP>')[0]+'<'
			items=striped.split('><')[1:-1]
			items=map(lambda x: x.split('='), items)
			print 'items for Text',items
			for item in items:
				#valveinfo=item[0].split('-')
				if item[0]=='St':
					#print int(valveinfo[1]),item[1]
					#self.valves[int(valveinfo[1])]['Gui'].setPixmap(self.ValvePixmaps[int(item[1])])
					self.addStuff(stateNames[int(item[1])])
		




class ConnectStuff(QtGui.QWidget):
	SerialDataOut = QtCore.pyqtSignal(object )
	def __init__(self,parent=None):
		super(ConnectStuff, self).__init__(parent)
		layout = QtGui.QVBoxLayout()
		self.b1 = QtGui.QPushButton("Teensy via USB")
		self.b1.clicked.connect(self.setoffACM)
		self.b2 = QtGui.QPushButton("Radio")
		self.b2.clicked.connect(self.setoffUSB)
		#self.b1.clicked.connect(self.btnstate)
		layout.addWidget(self.b1)
		layout.addWidget(self.b2)
		#self.timer = QTimer()
		self.setLayout(layout)
		self.console=None
#		try:
##			self.SerialConnn
		self.serialSream=''
		self.serial = None
		#self.timer.timeout.connect(self.tick)
		#self.timer.start(100)
		
		
	def setoffACM(self):
		print "hi there AMC"
		try:
			self.serial = serial.Serial('/dev/ttyACM0')
			self.serial.timeout = 0.001
			
			self.MyCommThread = CommsThread(self.serial)
            		self.MyCommThread.SerialThreadEvent.connect(self.tick)
            		self.MyCommThread.start()
		except:
			pass
	def setoffUSB(self):
		print "hi there USB"
		try:
			self.serial = serial.Serial('/dev/ttyUSB0',baudrate=57600)
			self.serial.timeout = 0.001
			
			self.MyCommThread = CommsThread(self.serial)
            		self.MyCommThread.SerialThreadEvent.connect(self.tick)
            		self.MyCommThread.start()
		except:
			pass		
		
	def tick(self,myinfo):
		print 'tick',myinfo
		#if myinfo[0]=='Packet':
		self.SerialDataOut.emit(myinfo)

		#print 'newline :',newline




class myWidget(QtGui.QMainWindow):
	def __init__(self,parent=None):
		super(myWidget, self).__init__(parent)
		self.resize(250, 150)
		self.setWindowTitle('Simple')
		self.widgetsTogetSerial=[]
		self.SerialConection=ConnectStuff()
		
		self.setCentralWidget(self.SerialConection)
		self.SerialConection.SerialDataOut.connect(self.handle_Telem)
		
		tab1	= myOutputText()	
#		tab2	= mysillyPics()
#		tab3	= QtGui.QWidget()
#		tab4	= QtGui.QWidget()



		ConsoleTabDock=QtGui.QDockWidget("Console",self)
		ConsoleTabDock.setWidget(tab1)
		self.widgetsTogetSerial.append(tab1)
		
		
#		PicTabDock=QtGui.QDockWidget("Pics",self)
#		PicTabDock.setWidget(tab2)
#		self.widgetsTogetSerial.append(tab2)
			
		self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,ConsoleTabDock)
#		self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,PicTabDock)
        
	
	def handle_Telem(self,info):
		print "handle_Telem"








def main():
    
    app = QtGui.QApplication(sys.argv)

    w = myWidget()
    w.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
