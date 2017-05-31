from PyQt5.QtGui import QKeyEvent, QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
import sys
import win32api as w32
from PIL import Image
from map import Map, Field
from player import Gamer, Enemy
from object import Bomb
from replay import Replay_system
from server import Connect
import time
import os.path


# todo lepsze tekstury, animacja wybuchu
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Bomberman")
        self.setWindowIcon(QIcon("icon.png"))
        self.width = 674
        self.height = 695
        screen_width = w32.GetSystemMetrics(0)
        screen_height = w32.GetSystemMetrics(1)
        self.setFixedSize(self.width, self.height)
        self.move((screen_width - self.width)/2, (screen_height - self.height)/2)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&Plik")
        new_a = fileMenu.addAction("Nowa gra")
        new_a.triggered.connect(self.new_action)
        multi_a = fileMenu.addAction("Gra multiplayer")
        multi_a.triggered.connect(self.multi_action)
        load_a = fileMenu.addAction("Wczytaj powtorke")
        load_a.triggered.connect(self.load_action)
        close_a = fileMenu.addAction("Zakoncz program")
        close_a.triggered.connect(self.close_action)
        self.system = Replay_system(self)
        self.screen = QGraphicsView(self)
        self.setCentralWidget(self.screen)
        self.canvas = QGraphicsScene()
        self.canvas.setSceneRect(0, 0, 672, 672)
        # todo ekran startowy, zamiast białego tła
        self.screen.setScene(self.canvas)
        self.auto = False
        self.running = False
        self.show()

    def close_action(self):
        sys.exit(0)

    def multi_action(self):
        self.multi_window = Connect(self)
        self.multi_window.show()

    def load_action(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        try:
            fileName, _ = QFileDialog.getOpenFileName(self, "Wybierz plik do odczytu", "", "Pliki XML (*.xml)",
                                                      options=options)
            self.replay = self.system.load_replay(fileName)
            lenght = len(self.replay)
            pop_time = self.replay[0][0]
            index = 1
            while True:
                if self.replay[index][0] == pop_time:
                    self.replay.pop(index)
                    index -= 1
                    lenght -= 1
                else:
                    pop_time = self.replay[index][0]
                index += 1
                if index == lenght:
                    break
            print("Pomyslnie wczytano powtorke")
            self.start_replay()
        except FileNotFoundError:
            print("Podany plik nie istnieje")

    def new_action(self):
        self.counter = 0
        self.replay = None
        self.W_key = False
        self.S_key = False
        self.A_key = False
        self.D_key = False
        self.mapa = Map()
        self.corners = {0: (self.mapa.real_left, self.mapa.real_top),
                        1: (self.mapa.real_right - 5 * Field.width, self.mapa.real_top),
                        2: (self.mapa.real_left, self.mapa.real_bottom - 5 * Field.height)}
        self.render_map()
        self.players = []
        self.players.append(Gamer(self.corners[0]))
        self.players.append(Enemy(self.corners[1]))
        self.players.append(Enemy(self.corners[2]))
        self.odrysuj = []
        self.obiekty = []
        self.xml_changes = []
        self.start_time = time.time()
        self.timer_render = QTimer(self)
        self.timer_render.timeout.connect(self.petla)
        self.stala = 1_000.0/60.0
        self.frames = 0
        self.updates = 0
        self.current_mili_time = lambda: int(round(time.time() * 1000))
        self.left_time = 0.0
        self.time = self.current_mili_time()
        self.title_timer = self.current_mili_time()
        self.system.create_file()
        self.first_frame = True
        self.running = True
        self.timer_render.start()

    def start_replay(self):
        self.render_replay_map()
        self.replay_timer = QTimer(self)
        self.replay_timer.timeout.connect(self.replay_render)
        self.index = 1
        self.replay_time_start = time.time()
        self.replay_timer.start()

    def replay_render(self):
        if not self.index == len(self.replay):
            if time.time() - self.replay_time_start >= float(self.replay[self.index][0]):
                self.canvas.clear()
                if not len(self.replay[self.index][1]) == 0:
                    for item in self.replay[self.index][1]:  # x, y, co do poprawienia
                        elem = Image.open(Map.type[int(item[2])].sprite)
                        self.rendered_map.paste(elem, (int(item[0]) * 16, int(item[1]) * 16))
                    self.rendered_map.save("mapa.png")
                # mapa
                mapa = QPixmap("mapa.png")
                test = QGraphicsPixmapItem()
                test.setPixmap(mapa)
                test.setPos(0, 0)
                test.setZValue(0)
                self.canvas.addItem(test)
                # gracz
                if not len(self.replay[self.index][2]) == 0:
                     for item in self.replay[self.index][2]:
                         if item[0] == '0':
                            sprite = QPixmap(Gamer.sprite)
                         else:
                             sprite = QPixmap(Enemy.sprite)
                         test = QGraphicsPixmapItem()
                         test.setPixmap(sprite)
                         test.setPos(int(item[1]), int(item[2]))
                         test.setZValue(5)
                         self.canvas.addItem(test)
                # bomby
                if not len(self.replay[self.index][3]) == 0:
                    for item in self.replay[self.index][3]:
                        sprite = QPixmap(Bomb.sprite)
                        test = QGraphicsPixmapItem()
                        test.setPixmap(sprite)
                        test.setPos(int(item[0]), int(item[1]))
                        test.setZValue(10)
                        self.canvas.addItem(test)
                self.index += 1
                # wybuch ?
        else:
            self.replay_timer.stop()
            print("Koniec powtorki. ")

    def keyPressEvent(self, event):
        if self.running:
            key = event.key()
            if key == Qt.Key_W or key == Qt.Key_Up:
                self.W_key = True
            elif key == Qt.Key_S or key == Qt.Key_Down:
                self.S_key = True
            elif key == Qt.Key_A or key == Qt.Key_Left:
                self.A_key = True
            elif key == Qt.Key_D or key == Qt.Key_Right:
                self.D_key = True
            elif key == Qt.Key_Q or key == Qt.Key_Space:
                if not self.auto:
                    self.obiekty.append(Bomb(self, self.players[0].xpos_left, self.players[0].ypos_top))
            elif key == Qt.Key_P:
                if self.auto:
                    self.auto = False
                else:
                    self.auto = True
            elif key == Qt.Key_Escape:
                self.petla_gry.exit()

    def keyReleaseEvent(self, event):
        if self.running:
            key = event.key()
            if key == Qt.Key_W or key == Qt.Key_Up:
                self.W_key = False
            elif key == Qt.Key_S or key == Qt.Key_Down:
                self.S_key = False
            elif key == Qt.Key_A or key == Qt.Key_Left:
                self.A_key = False
            elif key == Qt.Key_D or key == Qt.Key_Right:
                self.D_key = False

    def update(self):
        if self.auto:
            bomb_planted = self.players[0].ai_move(self.mapa, self)
            if bomb_planted is not None:
                self.obiekty.append(Bomb(self, bomb_planted[0], bomb_planted[1]))
        else:
            self.players[0].update(self.mapa, self)
        zakres = len(self.obiekty)
        if not zakres == 0:
            i = 0
            current_time = self.current_mili_time()
            while True:
                koniec = self.obiekty[i].update(self.mapa, self.players, current_time)
                if koniec == 1:
                    self.system.save_xml()
                    self.running = False
                    self.timer_render.stop()
                elif koniec == 0:
                    self.obiekty.pop(i)
                    i -= 1
                    zakres -= 1
                i += 1
                if i == zakres:
                    break

    def render(self):
        self.canvas.clear()
        if not len(self.odrysuj) == 0:
            for bomb in self.odrysuj:
                for item in bomb:  # x, y, co do poprawienia
                    elem = Image.open(Map.type[item[2]].sprite)
                    self.rendered_map.paste(elem, (item[0] * 16, item[1] * 16))
                    self.xml_changes.append(item)
            self.rendered_map.save("mapa.png")
        # mapa
        mapa = QPixmap("mapa.png")
        test = QGraphicsPixmapItem()
        test.setPixmap(mapa)
        test.setPos(0, 0)
        test.setZValue(0)
        self.canvas.addItem(test)
        # gracz
        if not len(self.players) == 0:
             for i in range(len(self.players)):
                 sprite = QPixmap(self.players[i].sprite)
                 test = QGraphicsPixmapItem()
                 test.setPixmap(sprite)
                 test.setPos(self.players[i].xpos_left, self.players[i].ypos_top)
                 test.setZValue(5)
                 self.canvas.addItem(test)
        # bomby
        if not len(self.obiekty) == 0:
            for i in range(len(self.obiekty)):
                sprite = QPixmap(self.obiekty[i].sprite)
                test = QGraphicsPixmapItem()
                test.setPixmap(sprite)
                test.setPos(self.obiekty[i].posx_left, self.obiekty[i].posy_top)
                test.setZValue(10)
                self.canvas.addItem(test)
        # wybuch ?
        self.odrysuj.clear()

    def petla(self):
        current_time = self.current_mili_time()
        self.left_time += (current_time - self.time) / self.stala
        self.time = current_time
        while self.left_time >= 1:
            self.update()
            if self.first_frame:
                self.system.save_frame(time.time() - self.start_time, self.mapa, self.players, self.obiekty, True)
                self.first_frame = False
            else:
                self.system.save_frame(time.time() - self.start_time, self.xml_changes, self.players, self.obiekty, False)
            self.xml_changes.clear()
            self.updates += 1
            self.left_time -= 1
        self.render()
        self.frames += 1
        if self.current_mili_time() - self.title_timer > 1000:
            self.title_timer += 1000
            self.setWindowTitle("Bomberman  ||  {0} fps  ||  {1} ups".format(self.frames, self.updates))
            self.frames = 0
            self.updates = 0

    def render_map(self):
        if not os.path.isfile("mapa.png"):
            self.rendered_map = Image.new('RGB', (16 * 42, 16 * 42))
        else:
            self.rendered_map = Image.open("mapa.png")
        for i in range(42):
            for j in range(42):
                elem = Image.open(Map.type[self.mapa.real_map[i][j]].sprite)
                self.rendered_map.paste(elem, (i * 16, j * 16))
        self.rendered_map.save("mapa.png")

    def render_replay_map(self):
        if not os.path.isfile("mapa.png"):
            self.rendered_map = Image.new('RGB', (16 * 42, 16 * 42))
        else:
            self.rendered_map = Image.open("mapa.png")
        for item in self.replay[0][1]:
            elem = Image.open(Map.type[int(float(item[2]))].sprite)
            self.rendered_map.paste(elem, (int(item[0]) * 16, int(item[1]) * 16))
        self.rendered_map.save("mapa.png")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gra = MainWindow()
    gra.show()
    sys.exit(app.exec_())

