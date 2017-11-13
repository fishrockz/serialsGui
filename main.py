import sys,select

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from PyQt4 import QtGui
from PyQt4 import QtCore

from multiprocessing import Pipe
import serial,time




class ConsoleSimples(QtGui.QWidget):
	SerialDataOut = QtCore.pyqtSignal(object )
	def __init__(self,parent=None):
		super(ConsoleSimples, self).__init__(parent)
		
		MainLayout = QtGui.QVBoxLayout()
		self.buttonSend = QtGui.QPushButton("Send")
		self.textSend = QtGui.QLineEdit(parent)
		self.layoutSend = QtGui.QHBoxLayout()
		self.layoutSend.addWidget(self.buttonSend)
		self.layoutSend.addWidget(self.textSend)
		MainLayout.addLayout(self.layoutSend)

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
		self.addStuff(info)
		return
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
		
class CommsThread(QtCore.QThread):
	SerialThreadEvent = QtCore.pyqtSignal(object)
	def __init__(self, portname,transmitPipe=None):
		QtCore.QThread.__init__(self)
		self.serialSream=''
		self._FileObject=serial.Serial(portname, timeout=0)
		self._transmitPipe=transmitPipe
	def run(self):	
		while 1:
			newline=''
			if self._FileObject !=None:
				#try:
					print "select"
					readobjects=[self._FileObject,]
					if self._transmitPipe: readobjects+=self._transmitPipe
					print "from",readobjects
					myselect=select.select(readobjects,[],[])
					print 'select:',myselect
					new = self._FileObject.read()
					while new != '':
						newline+=new
						
						new = self._FileObject.read()
					print 'new: ','"'+str(newline.encode('string_escape'))+'"',type(newline)
				
				#except:
				#	pass
			else:
		 		pass
				#end thread?
			print "bop"
			self.serialSream+=newline
			while '\n' in self.serialSream:
				bits=self.serialSream.split('\n')
				fulline=bits[0]
				fulline=fulline.replace('\r','')
				print 'new line: ',str(fulline.encode('string_escape'))+'"',type(fulline)
				self.serialSream='\n'.join(bits[1:])
				self.SerialThreadEvent.emit(fulline)

				


class SerialConnection(QtGui.QWidget):
	
	def __init__(self,parent=None,name='',port='/dev/ttyACM0',trigger=None):
		super(SerialConnection, self).__init__(parent)
		layout = QtGui.QHBoxLayout()
		self._port=port
		self._SerialDataOut=trigger
		self._name=name
		self._active=0
		self._transmitePipe=None
		self.b1 = QtGui.QPushButton("Teensy via "+name)
		self.b1.clicked.connect(self.setoffPort)
		layout.addWidget(self.b1)
		self.setLayout(layout)
	def setoffPort(self):
		print "hi there "+self._name
		if self._active: return
	#	try:
		if 1:
			self._transmitePipe=Pipe()
			self.MyCommThread = CommsThread(self._port,self._transmitePipe)
            		self.MyCommThread.SerialThreadEvent.connect(self.SerialCallback)
            		self.MyCommThread.start()
            		self._active=1
	#	except:
	#		pass
	def SerialCallback(self,packet):
		if self._SerialDataOut:
			self._SerialDataOut.emit(packet)	
class ConnectStuff(QtGui.QWidget):
	SerialDataOut = QtCore.pyqtSignal(object )
	def __init__(self,parent=None):
		super(ConnectStuff, self).__init__(parent)
		layout = QtGui.QVBoxLayout()
		self.b1=SerialConnection(name='USB',port='/dev/ttyACM0',trigger=self.SerialDataOut)
		self.b2=SerialConnection(name='Radio',port='/dev/ttyUSB0',trigger=self.SerialDataOut)
		layout.addWidget(self.b1)
		layout.addWidget(self.b2)
		self.setLayout(layout)
		





class myWidget(QtGui.QMainWindow):
	def __init__(self,parent=None):
		super(myWidget, self).__init__(parent)
		self.resize(250, 150)
		self.setWindowTitle('Simple')
		self.widgetsTogetSerial=[]
		self.SerialConection=ConnectStuff()
		
		self.setCentralWidget(self.SerialConection)
		self.SerialConection.SerialDataOut.connect(self.handle_Packet)
		
		tab1	= ConsoleSimples()
		self.add_widgit(tab1)


		for widget in self.widgetsTogetSerial:
		    defaultpos=QtCore.Qt.BottomDockWidgetArea
		    self.addDockWidget(defaultpos,widget.CTB)
        
	def add_widgit(self,widget):
	    ConsoleTabDock=QtGui.QDockWidget("Console",self)
	    ConsoleTabDock.setWidget(widget)
	    widget.CTB=ConsoleTabDock

	    widget.SerialDataOut.connect(self.handle_Packet)

	    self.widgetsTogetSerial.append(widget)
	def handle_Packet(self,info):
		print "handle_Packet"
		for widget in self.widgetsTogetSerial:
			if hasattr(widget, 'SerialRecive'):
				widget.SerialRecive(info)








def main():
    
    app = QtGui.QApplication(sys.argv)

    w = myWidget()
    w.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
