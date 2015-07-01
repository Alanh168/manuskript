#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.editors.editorWidget_ui import *
from ui.editors.fullScreenEditor import *
from ui.editors.textFormat import *
from ui.views.textEditView import *
from functions import *
import settings

class editorWidget(QWidget, Ui_editorWidget_ui):
    
    toggledSpellcheck = pyqtSignal(bool)
    dictChanged = pyqtSignal(str)
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.currentIndex = QModelIndex()
        self.currentID = None
        self.txtEdits = []
        self.scroll.setBackgroundRole(QPalette.Base)
        self.toggledSpellcheck.connect(self.txtRedacText.toggleSpellcheck, AUC)
        self.dictChanged.connect(self.txtRedacText.setDict, AUC)
        self.txtRedacText.setHighlighting(True)
        self.currentDict = ""
        self.spellcheck = True
        self.folderView = "cork"
        self.mw = mainWindow()
        
    #def setModel(self, model):
        #self._model = model
        #self.setView()
        
    def setFolderView(self, v):
        oldV = self.folderView
        if v == "cork":
            self.folderView = "cork"
        elif v == "outline":
            self.folderView = "outline"
        else:
            self.folderView = "text"
            
        # Saving value
        settings.folderView = self.folderView
            
        if oldV != self.folderView and self.currentIndex:
            self.setCurrentModelIndex(self.currentIndex)
        
    def setCorkSizeFactor(self, v):
        self.corkView.itemDelegate().setCorkSizeFactor(v)
        self.redrawCorkItems()
        
    def redrawCorkItems(self):
        r = self.corkView.rootIndex()
        
        if r.isValid():
            count = r.internalPointer().childCount()
        else:
            count = self.mw.mdlOutline.rootItem.childCount()
        
        for c in range(count):
            self.corkView.itemDelegate().sizeHintChanged.emit(r.child(c, 0))
        
    def setView(self):
        #index = mainWindow().treeRedacOutline.currentIndex()
        
        ## Couting the number of other selected items
        #sel = []
        #for i in mainWindow().treeRedacOutline.selectionModel().selection().indexes():
            #if i.column() != 0: continue
            #if i not in sel: sel.append(i)
        
        #if len(sel) != 0:
            #item = index.internalPointer()
        #else:
            #index = QModelIndex()
            #item = self.mw.mdlOutline.rootItem
            
        #self.currentIndex = index
        
        if self.currentIndex.isValid():
            item = self.currentIndex.internalPointer()
        else:
            item = self.mw.mdlOutline.rootItem
            
        def addTitle(itm):
            edt = textEditView(self, html="<h{l}>{t}</h{l}>".format(l=min(itm.level()+1, 5), t=itm.title()), autoResize=True)
            edt.setFrameShape(QFrame.NoFrame)
            self.txtEdits.append(edt)
            l.addWidget(edt)
        
        def addLine():
            line = QFrame(self.text)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            l.addWidget(line)
        
        def addText(itm):
            edt = textEditView(self, 
                               index=itm.index(), 
                               spellcheck=self.spellcheck, 
                               dict=settings.dict,
                               highlighting=True,
                               autoResize=True)
            edt.setFrameShape(QFrame.NoFrame)
            edt.setStatusTip("{} ({})".format(itm.path(), itm.type()))
            self.toggledSpellcheck.connect(edt.toggleSpellcheck, AUC)
            self.dictChanged.connect(edt.setDict, AUC)
            #edt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.txtEdits.append(edt)
            l.addWidget(edt)
        
        def addChildren(itm):
            for c in range(itm.childCount()):
                child = itm.child(c)
                
                if child.isFolder():
                    addTitle(child)
                    addChildren(child)
                    
                else:
                    addText(child)
                    addLine()
        
        def addSpacer():
            l.addItem(QSpacerItem(10, 1000, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
        # Display multiple selected items
        #if len(sel) > 1 and False:  # Buggy and not very useful, skip
            #self.stack.setCurrentIndex(1)
            #w = QWidget()
            #l = QVBoxLayout(w)
            #self.txtEdits = []
            #for idx in sel:
                #sItem = idx.internalPointer()
                #addTitle(sItem)
                #if sItem.isFolder():
                    #addChildren(sItem)
                #else:
                    #addText(sItem)
                #addLine()
            #addSpacer()
            #self.scroll.setWidget(w)
            
        if item and item.isFolder() and self.folderView == "text":
            self.stack.setCurrentIndex(1)
            
            w = QWidget()
            l = QVBoxLayout(w)
            #self.scroll.setWidgetResizable(False)
            
            self.txtEdits = []
            
            if item != self.mw.mdlOutline.rootItem:
                addTitle(item)
                
            addChildren(item)
            addSpacer()
            self.scroll.setWidget(w)
            
        elif item and item.isFolder() and self.folderView == "cork":
            self.stack.setCurrentIndex(2)
            self.corkView.setModel(self.mw.mdlOutline)
            self.corkView.setRootIndex(self.currentIndex)
            self.corkView.selectionModel().selectionChanged.connect(
                lambda: mainWindow().redacMetadata.selectionChanged(self.corkView), AUC)
            self.corkView.clicked.connect(
                lambda: mainWindow().redacMetadata.selectionChanged(self.corkView), AUC)
            
        elif item and item.isFolder() and self.folderView == "outline":
            self.stack.setCurrentIndex(3)
            self.outlineView.setModelPersos(mainWindow().mdlPersos)
            self.outlineView.setModelLabels(mainWindow().mdlLabels)
            self.outlineView.setModelStatus(mainWindow().mdlStatus)
            self.outlineView.setModel(self.mw.mdlOutline)
            self.outlineView.setRootIndex(self.currentIndex)
            self.outlineView.selectionModel().selectionChanged.connect(
                lambda: mainWindow().redacMetadata.selectionChanged(self.outlineView), AUC)
            self.outlineView.clicked.connect(
                lambda: mainWindow().redacMetadata.selectionChanged(self.outlineView), AUC)
            
        else:
            self.txtRedacText.setCurrentModelIndex(self.currentIndex)
            self.stack.setCurrentIndex(0) # Single text item
        
        try:
            self.mw.mdlOutline.dataChanged.connect(self.modelDataChanged, AUC)
            self.mw.mdlOutline.rowsInserted.connect(self.updateIndexFromID, AUC)
            self.mw.mdlOutline.rowsRemoved.connect(self.updateIndexFromID, AUC)
        except TypeError:
            pass
        
        self.updateStatusBar()
        
        
    def setCurrentModelIndex(self, index=None):
        if index.isValid():
            self.currentIndex = index
            self.currentID = self.mw.mdlOutline.ID(index)
            #self._model = index.model()
        else:
            self.currentIndex = QModelIndex()
            
        self.setView()
        
    def updateIndexFromID(self):
        idx = self.mw.mdlOutline.getIndexByID(self.currentID)
        if idx != self.currentIndex:
            self.currentIndex = idx
            self.setView()
            
    def modelDataChanged(self, topLeft, bottomRight):
        #if self.currentID:
            #self.updateIndexFromID()
        if not self.currentIndex:
            return
        if topLeft.row() <= self.currentIndex.row() <= bottomRight.row():
            self.updateStatusBar()
            
    def updateStatusBar(self):
        # Update progress
        #if self.currentIndex and self.currentIndex.isValid():
        #if self._model:
        mw = mainWindow()
        if not mw: return
        
        mw.mainEditor.updateStats()
            
    def toggleSpellcheck(self, v):
        self.spellcheck = v
        self.toggledSpellcheck.emit(v)
        
    def setDict(self, dct):
        self.currentDict = dct
        self.dictChanged.emit(dct)
        
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Escape, Qt.Key_F11] and self._fullscreen:
            mainWindow().show()
            self.stack.setStyleSheet("")
            self.setGeometry(self._geometry)
            self.setParent(self._parent)
            self._parent.layout().insertWidget(1, self)
            self._fullscreen = False
        else:
            QWidget.keyPressEvent(self, event)