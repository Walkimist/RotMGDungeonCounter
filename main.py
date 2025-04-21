from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QComboBox, QGraphicsOpacityEffect, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path
import sys, os, pickle

darkStylesheet = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
}

QLabel {
    color: #f0f0f0;
}

QComboBox, QScrollArea, QMainWindow {
    background-color: #3c3f41;
    color: #f0f0f0;
    border: 1px solid #555;
}

QComboBox QAbstractItemView {
    background-color: #2b2b2b;
    selection-background-color: #505050;
}

QScrollBar:vertical {
    background: #000000;
    width: 2px;
}

QScrollBar::handle:vertical {
    background: #5c5c5c;
    min-height: 4px;
}
"""

dungeons = []
ALLDUNGEONS = ["Pirate Cave" , "Forest Maze" , "Spider Den" , "Snake Pit" , "Forbidden Jungle" , "The Hive" , "Ancient Ruins" , "Magic Woods" , "Sprite World" , "Candyland Hunting Grounds" , "Cave of a Thousand Treasures" , "Undead Lair" , "Abyss of Demons" , "Manor of the Immortals" , "Puppet Master’s Theatre" , "Toxic Sewers" , "Cursed Library" , "Haunted Cemetery" , "Mad Lab" , "Parasite Chambers" , "Davy Jones’ Locker" , "Mountain Temple" , "The Third Dimension" , "Lair of Draconis" , "Deadwater Docks" , "Woodland Labyrinth" , "The Crawling Depths" , "Ocean Trench" , "Ice Cave" , "Tomb of the Ancients" , "Fungal Cavern" , "Crystal Cavern" , "The Nest" , "The Shatters" , "Lost Halls" , "Cultist Hideout" , "The Void" , "Sulfurous Wetlands" , "Kogbold Steamworks" , "Oryx’s Castle" , "Lair of Shaitan" , "Puppet Master’s Encore" , "Cnidarian Reef" , "Secluded Thicket" , "High Tech Terror" , "Oryx’s Chamber" , "Wine Cellar" , "Oryx’s Sanctuary" , "Belladonna’s Garden" , "Ice Tomb" , "Mad God Mayhem" , "Battle for the Nexus" , "Santa’s Workshop" , "The Machine" , "Malogia" , "Untaris" , "Forax" , "Katalund" , "Rainbow Road" , "Beachzone" , "Spectral Penitentiary"]
COLLECTIONS = ["Tunnel Rat", "Explosive Journey", "Travel of the Decade", "First Steps", "King of the Mountains", "Conqueror of the Realm", "Enemy of the Court", "Epic Battles", "Far Out", "Hero of the Nexus", "Season’s Beatins", "Realm of the Mad God"]
SAVEFILE = 'save.pickle'

def createSave(path):
    p = f"saves/{path}"
    if not os.path.exists(p):
        print("Save file not found, creating new file.")
        f = open(f"{p}", "x")
        f.close()
    return p

def saveData(path):
    p = f"saves/{path}"
    with open(p, 'wb') as f:
        pickle.dump({dungeon.name: dungeon.isComplete for dungeon in dungeons}, f)

def loadData(path):
    p = f"saves/{path}"
    if not os.path.exists(p):
        return
    
    with open(p, 'rb') as f:
        try:
            data = pickle.load(f)
            for dungeon in dungeons:
                if dungeon.name in data:
                    dungeon.isComplete = data[dungeon.name]
        except Exception as e:
            #print(f"Failed to load save data: {e}")
            pass

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2b2b2b;")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        self.title = QLabel("RotMG Completion Tracker")
        self.title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.title)

        layout.addStretch()

        self.minimizeBtn = QLabel('-')
        self.minimizeBtn.setStyleSheet("color: white; font-size: 18px; padding: 4px;")
        self.minimizeBtn.setAlignment(Qt.AlignCenter)
        self.minimizeBtn.setFixedSize(20, 20)
        self.minimizeBtn.mousePressEvent = self.minimize

        self.closeBtn = QLabel("×")
        self.closeBtn.setStyleSheet("color: white; font-size: 18px; padding: 4px;")
        self.closeBtn.setAlignment(Qt.AlignCenter)
        self.closeBtn.setFixedSize(20, 20)
        self.closeBtn.mousePressEvent = self.close

        layout.addWidget(self.minimizeBtn)
        layout.addWidget(self.closeBtn)

        self.setLayout(layout)

        self.oldPos = None

    def close(self, event):
        self.parent.close()
    
    def minimize(self, event):
        self.parent.showMinimized()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

class ResizableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._resizing = False
        self._resizeDir = None
        self._mousePos = None
        self.MARGIN = 8
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePos = event.globalPos()
            self._resizeDir = self.getResizeDirection(event.pos())
            if self._resizeDir:
                self._resizing = True
            else:
                self._resizing = False
    
    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resizeDir = None

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.globalPos() - self._mousePos
            geom = self.geometry()

            if 'left' in self._resizeDir:
                geom.setLeft(geom.left() + delta.x())
            if 'right' in self._resizeDir:
                geom.setRight(geom.right() + delta.x())
            if 'top' in self._resizeDir:
                geom.setTop(geom.top() + delta.y())
            if 'bottom' in self._resizeDir:
                geom.setBottom(geom.bottom() + delta.y())

            self.setGeometry(geom)
            self._mousePos = event.globalPos()
        else:
            cursor = self.getCursorShape(event.pos())
            self.setCursor(cursor)

    def getResizeDirection(self, pos):
        rect = self.rect()
        direction = ""

        if pos.x() <= self.MARGIN:
            direction += "left"
        elif pos.x() >= rect.width() - self.MARGIN:
            direction += "right"
        if pos.y() <= self.MARGIN:
            direction += "top"
        elif pos.y() >= rect.height() - self.MARGIN:
            direction += "bottom"
        
        return direction if direction else None

    def getCursorShape(self, pos):
        dir = self.getResizeDirection(pos)
        return Qt.ArrowCursor

class Character():
    name = ''
    savePath = ''
    icon = ''

    def __init__(self, name, icon):
        self.name = name
        self.savePath = createSave(name)
        self.icon = f"assets\\characters\\{icon}.png"

    def load(self):
        pass

class Dungeon:
    name = ''
    collection = []
    icon = ''
    isComplete = False

    def __init__(self, name):
        self.name = name

        coll = []
        if (name in ["Pirate Cave" , "Forbidden Jungle" , "Spider Den" , "Snake Pit" , "Undead Lair" , "Abyss of Demons" , "Manor of the Immortals" , "Ocean Trench" , "Tomb of the Ancients" , "Oryx’s Castle" , "Oryx’s Chamber" , "Wine Cellar"]):
            coll.append("Tunnel Rat")
        if (name in ["Davy Jones’ Locker" , "Mad Lab" , "Candyland Hunting Grounds" , "Haunted Cemetery" , "Cave of a Thousand Treasures" , "Lair of Draconis" , "Deadwater Docks" , "Woodland Labyrinth" , "The Crawling Depths" , "The Shatters" , "Lair of Shaitan" , "Puppet Master’s Theatre" , "Ice Cave"]):
            coll.append("Explosive Journey")
        if (name in ["Puppet Master’s Encore" , "The Hive" , "Toxic Sewers" , "Mountain Temple" , "The Third Dimension" , "The Nest" , "Lost Halls" , "Cultist Hideout" , "The Void" , "Cnidarian Reef" , "Parasite Chambers" , "Magic Woods" , "Secluded Thicket" , "Cursed Library" , "Oryx’s Sanctuary" , "Ancient Ruins" , "High Tech Terror" , "Sulfurous Wetlands" , "Spectral Penitentiary"]):
            coll.append("Travel of the Decade")
        if (name in ["Pirate Cave" , "Forest Maze" , "Forbidden Jungle" , "Spider Den" , "The Hive"]):
            coll.append("First Steps")
        if (name in ["Snake Pit" , "Sprite World" , "Abyss of Demons" , "Toxic Sewers" , "Mad Lab" , "Magic Woods" , "Puppet Master’s Theatre" , "Haunted Cemetery" , "Cursed Library" , "Ancient Ruins" , "Sulfurous Wetlands" , "Spectral Penitentiary"]):
            coll.append("King of the Mountains")
        if (name in ["Davy Jones’ Locker" , "Ice Cave" , "Lair of Draconis" , "Mountain Temple" , "The Third Dimension" , "Ocean Trench" , "Tomb of the Ancients" , "The Shatters" , "The Nest" , "Fungal Cavern" , "Crystal Cavern" , "Lost Halls" , "Kogbold Steamworks"]):
            coll.append("Conqueror of the Realm")
        if (name in ["Lair of Shaitan" , "Puppet Master’s Encore" , "Cnidarian Reef" , "Secluded Thicket" , "High Tech Terror"]):
            coll.append("Enemy of the Court")
        if (name in ["Deadwater Docks" , "Woodland Labyrinth" , "The Crawling Depths" , "The Nest" , "Secluded Thicket"]):
            coll.append("Epic Battles")
        if (name in ["Malogia" , "Untaris" , "Forax" , "Katalund"]):
            coll.append("Far Out")
        if (name in ["Pirate Cave" , "Forest Maze" , "Spider Den" , "Snake Pit" , "Forbidden Jungle" , "The Hive" , "Ancient Ruins" , "Magic Woods" , "Sprite World" , "Candyland Hunting Grounds" , "Cave of a Thousand Treasures" , "Undead Lair" , "Abyss of Demons" , "Manor of the Immortals" , "Puppet Master’s Theatre" , "Toxic Sewers" , "Cursed Library" , "Haunted Cemetery" , "Mad Lab" , "Parasite Chambers" , "Davy Jones’ Locker" , "Mountain Temple" , "The Third Dimension" , "Lair of Draconis" , "Deadwater Docks" , "Woodland Labyrinth" , "The Crawling Depths" , "Ocean Trench" , "Ice Cave" , "Tomb of the Ancients" , "Fungal Cavern" , "Crystal Cavern" , "The Nest" , "The Shatters" , "Lost Halls" , "Cultist Hideout" , "The Void" , "Sulfurous Wetlands" , "Kogbold Steamworks" , "Oryx’s Castle" , "Lair of Shaitan" , "Puppet Master’s Encore" , "Cnidarian Reef" , "Secluded Thicket" , "High Tech Terror" , "Oryx’s Chamber" , "Wine Cellar" , "Oryx’s Sanctuary" , "Spectral Penitentiary"]):
            coll.append("Hero of the Nexus")
        if (name in ["Belladonna’s Garden" , "Ice Tomb" , "Mad God Mayhem" , "Battle for the Nexus" , "Santa’s Workshop" , "The Machine" , "Malogia" , "Untaris" , "Forax" , "Katalund" , "Rainbow Road" , "Beachzone"]):
            coll.append("Season’s Beatins")
        if (name in ["Pirate Cave" , "Forest Maze" , "Spider Den" , "Snake Pit" , "Forbidden Jungle" , "The Hive" , "Ancient Ruins" , "Magic Woods" , "Sprite World" , "Candyland Hunting Grounds" , "Cave of a Thousand Treasures" , "Undead Lair" , "Abyss of Demons" , "Manor of the Immortals" , "Puppet Master’s Theatre" , "Toxic Sewers" , "Cursed Library" , "Haunted Cemetery" , "Mad Lab" , "Parasite Chambers" , "Davy Jones’ Locker" , "Mountain Temple" , "The Third Dimension" , "Lair of Draconis" , "Deadwater Docks" , "Woodland Labyrinth" , "The Crawling Depths" , "Ocean Trench" , "Ice Cave" , "Tomb of the Ancients" , "Fungal Cavern" , "Crystal Cavern" , "The Nest" , "The Shatters" , "Lost Halls" , "Cultist Hideout" , "The Void" , "Sulfurous Wetlands" , "Kogbold Steamworks" , "Oryx’s Castle" , "Lair of Shaitan" , "Puppet Master’s Encore" , "Cnidarian Reef" , "Secluded Thicket" , "High Tech Terror" , "Oryx’s Chamber" , "Wine Cellar" , "Oryx’s Sanctuary" , "Belladonna’s Garden" , "Ice Tomb" , "Mad God Mayhem" , "Battle for the Nexus" , "Santa’s Workshop" , "The Machine" , "Malogia" , "Untaris" , "Forax" , "Katalund" , "Rainbow Road" , "Beachzone" , "Spectral Penitentiary"]):
            coll.append("Realm of the Mad God")

        self.collection = coll
        self.icon = f"assets\\dungeons\\{name}.png"

class DungeonWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, dungeon):
        super().__init__()
        layout = QHBoxLayout()

        self.dungeon = dungeon

        self.image = QLabel(self)
        pixmap = QPixmap(dungeon.icon)
        resizedPixmap = pixmap.scaled(50,50, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image.setPixmap(resizedPixmap)
        self.image.setScaledContents(False)

        self.label = QLabel(dungeon.name)

        self.updateStyle()

        layout.addWidget(self.image)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.dungeon.isComplete = not self.dungeon.isComplete
        self.updateStyle()
        saveData(SAVEFILE)
        self.clicked.emit()
    
    def updateStyle(self):
        if self.dungeon.isComplete:
            opacity = QGraphicsOpacityEffect()
            opacity.setOpacity(0.4)
            self.image.setGraphicsEffect(opacity)
            self.label.setStyleSheet("color: #3b3b3b;")
        else:
            self.image.setGraphicsEffect(None)
            self.label.setStyleSheet("color: #f0f0f0;")

class CollectionViewer(ResizableWindow):
    def __init__(self, dungeons):
        super().__init__()
        self.dungeons = dungeons

        self.dropDown = QComboBox()
        self.dropDown.addItems(COLLECTIONS)
        self.dropDown.setMaxVisibleItems(len(COLLECTIONS))
        self.dropDown.currentTextChanged.connect(self.parseDungeons)
        self.dropDown.currentTextChanged.connect(self.checkIfCompleted)

        self.hideCompleted = QCheckBox("Hide completed")
        self.hideCompleted.stateChanged.connect(self.changeHideState)
        self.hideState = False

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.collectionStatus = QLabel()

        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.scroll.setWidget(self.content)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        self.titleBar = TitleBar(self)
        mainLayout.addWidget(self.titleBar)

        contentLayout = QVBoxLayout()
        contentLayout.addWidget(self.hideCompleted)
        contentLayout.addWidget(self.dropDown)
        contentLayout.addWidget(self.scroll)
        contentLayout.addWidget(self.collectionStatus)

        contentWidget = QWidget()
        contentWidget.setLayout(contentLayout)
        mainLayout.addWidget(contentWidget)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

        self.parseDungeons("Tunnel Rat")
        self.checkIfCompleted("Tunnel Rat")
        self.selected = "Tunnel Rat"

    def displayDungeons(self, dungeons):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for dungeon in dungeons:
            self.layout.addWidget(DungeonWidget(dungeon))

    def parseDungeons(self, selected):
        parsedDungeons = []
        self.selected = selected

        for dungeon in self.dungeons:
            if selected in dungeon.collection:
                if self.hideState:
                    if not dungeon.isComplete:
                        parsedDungeons.append(dungeon)
                else:
                    parsedDungeons.append(dungeon)

        self.displayDungeons(parsedDungeons)
    
    def checkIfCompleted(self, selected):
        completed = True

        for dungeon in self.dungeons:
            if selected in dungeon.collection:
                if not dungeon.isComplete:
                    completed = False

        if completed:
            self.collectionStatus.setStyleSheet("color: #44db74;")
            self.collectionStatus.setText(f"{selected} - COMPLETE")
        else:
            self.collectionStatus.setStyleSheet("color: #db444c;")
            self.collectionStatus.setText(f"{selected} - INCOMPLETE")

        self.changeHideState(self.hideState)
    def changeHideState(self, state):
        if state == 2:
            self.hideState = True
        elif state == 0:
            self.hideState = False
        else:
            self.hideState = state
        self.parseDungeons(self.selected)

    def mouseReleaseEvent(self, event):
        self.checkIfCompleted(self.selected)

def window():
    app = QApplication(sys.argv)
    app.setStyleSheet(darkStylesheet)
    win = CollectionViewer(dungeons)
    win.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    win.setGeometry(800, 300, 280, 600)
    win.setMinimumWidth(280)
    win.show()
    sys.exit(app.exec_())

createSave(SAVEFILE)

for dungeonName in ALLDUNGEONS:
    dg = dungeons.append(Dungeon(dungeonName))

loadData(SAVEFILE)

window()