from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from mainwindow import Ui_MainWindow


from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Note(Base):
    __tablename__= 'note'
    id = Column(Integer, primary_key=True)
    text = Column(String(1000), nullable=False)
    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)

engine = create_engine('sqlite:///notes.db')
    # Initalize the database if it is not already.
    #if not engine.dialect.has_table(engine, "note"):
Base.metadata.create_all(engine)


# Create a session for updates and crud operations
Session = sessionmaker(bind=engine)
session = Session()

_NOTES = {}

def create_note():
    mainwindow()

class mainwindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
    # invoking the mom class
        super(mainwindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.show()

        #loading notes or saving new ones
        if obj:
            self.obj = obj 
            self.load()
        else:
            self.obj = Note()
            self.save()
        
        self.closeButton.pressed.connect(self.delete_window)
        self.addButton.pressed.connect(create_note)
        self.textEdit.textChanged.connect(self.save)

        # flag
        self._drag_active = False 


    def load(self):
        self.move(self.obj.x, self.obj.y)
        self.textEdit.setHtml(self.obj.text)
        _NOTES[self.obj.id] = self 

    def save(self):
        self.obj.x = self.x()
        self.obj.y = self.y()
        self.obj.text = self.textEdit.toHtml() 
        session.add(self.obj)
        session.commit()
        _NOTES [self.obj.id]=self   

    def mousePressEvent(self, e):
        self.previous_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        delta = e.globalPos() - self.previous_pos
        self.move(self.x()+delta.x(), self.y()+delta.y())
        self.previous_pos = e.globalPos()

        self._drag_active = True             
    
    def mouseReleaseEvent(self, e):
        if self._drag_active:
            self.save()
            self._drag_active = False 
    def delete_window(self):
        result = QMessageBox.question(self, "Confirme Delete", "Are you sure to delete this note?")
        if result == QMessageBox.Yes:
            session.delete(self.obj)
            session.commit()
            self.close()



if __name__ == '__main__':
    remindernote = QApplication([])
    remindernote.setApplicationName("Remind me!")
    remindernote.setStyle("Fusion")

# Styling the window
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(47, 162, 204))
    palette.setColor(QPalette.WindowText, QColor(190,170,164))
    palette.setColor(QPalette.ButtonText, QColor(190,170,164))
    palette.setColor(QPalette.Text, QColor(11, 11, 13))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(219, 13, 51))
    
    remindernote.setPalette(palette)

#no notes saved yet
    saved_notes = session.query(Note).all()
    if len(saved_notes) == 0:
        mainwindow()
    else:
        for note in saved_notes:
            mainwindow(obj=note)   




    remindernote.exec()    