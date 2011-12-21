# -*- coding: utf-8 -*-
import numpy.core.multiarray

import sys, os, time, urllib
import shutil, datetime

from PyQt4 import QtCore, QtGui, Qt

from main_ui import Ui_MainWindow
import images_rc

ROOT_PATH = os.getcwd()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

def get_world_name():
    return filter(lambda x: 'level-name' in x, open('server.properties','r').read().split('\n'))[0].split('=')[-1]

class MyForm(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setupUi(self)

        self.setWindowTitle('GokyAdmin')
        self.setWindowIcon(QtGui.QIcon(':/png/icon.png'))   

        self.icon = QtGui.QSystemTrayIcon(QtGui.QIcon(':/png/icon.png'))
        self.icon.setToolTip(get_world_name())
        
        self.icon.activated.connect(self.toggleWindow)
        self.icon.show()

        self.server = QtCore.QProcess(self)
        self.server.readyReadStandardOutput.connect(self.updateOutput)
        self.server.readyReadStandardError.connect(self.updateError)
        self.server.finished.connect(self.updateExit)
        
        self.initialize()
    
    def toggleWindow(self, reason):
        if reason == 3: #click
            self.setVisible(not self.isVisible())

    def check_login(self, text):
        print text
        if 'logged in with entity id' in text:
            user_name = text[text.find("[INFO]")+7:].split()[0]
            self.update_login(user_name)

    def updateOutput(self):
        update = _fromUtf8(self.server.readAllStandardOutput())
        self.check_login(str(update))
        self.text.append(update)
    
    def updateError(self):
        update = _fromUtf8(self.server.readAllStandardError())
        self.check_login(str(update))
        self.text.append(update)

    def updateExit(self):
        print 'EXIT'
        self.text.append("MAJOR ERROR - SERVER EXITED!")

    def initialize(self):
        self.text.append('Backing up world')
        try:
            self.backup()
        except Exception as e:
            if 'Error 183' in str(e):
                self.text.append('Backup already exists! Skipping...')
            else:
                self.text.append('Backup failed! Error : ' + str(e))
        else:
            self.text.append('Backup done!')
        self.text.append('Starting server...')

        self.server.start('java  -Xmx1024M -Xms1024M -jar minecraft_server.jar nogui')
        #self.server.start('compile_qt.bat')


    def backup(self):
        world_name = get_world_name()
        shutil.copytree(os.path.join(ROOT_PATH, world_name), os.path.join(ROOT_PATH, world_name+datetime.datetime.now().strftime("_%Y_%m_%d")))

    def update_login(self, name):
        self.icon.showMessage(name, 'Logged in at ' + get_world_name(),0)


def kill_process(app):
    app.server.kill()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    #myapp.show()
    app.lastWindowClosed.connect(lambda : kill_process(myapp))
    sys.exit(app.exec_())