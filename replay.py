import xml.dom.minidom as minidom
from os import path


class Replay_system:
    def __init__(self, parent=None):
        self.parent = parent

    def create_file(self):
        index = 0
        while True:
            self.link = "data" + str(index) + ".xml"
            if path.isfile(self.link):
                index += 1
                continue
            break
        self.file = minidom.Document()
        root = self.file.createElement("game")
        self.file.appendChild(root)

    def save_frame(self, czas, changes, players, obiekty, pierwsza):
        frame = self.file.createElement("frame")
        frame.setAttribute("time", str(czas))
        zn_mapa = self.file.createElement("mapa")
        if pierwsza:
            for x in range(42):
                for y in range(42):
                    pole = self.file.createElement("pole")
                    pole.setAttribute("x", str(x))
                    pole.setAttribute("y", str(y))
                    text = self.file.createTextNode(str(changes.real_map[x][y]))
                    pole.appendChild(text)
                    zn_mapa.appendChild(pole)
        else:
            if not len(changes) == 0:
                for i in changes:
                    pole = self.file.createElement("pole")
                    pole.setAttribute("x", str(i[0]))
                    pole.setAttribute("y", str(i[1]))
                    text = self.file.createTextNode(str(i[2]))
                    pole.appendChild(text)
                    zn_mapa.appendChild(pole)
        frame.appendChild(zn_mapa)
        zn_gracze = self.file.createElement("gracze")
        for i in range(len(players)):
            gracz = self.file.createElement("gracz")
            gracz.setAttribute("id", str(i))
            wspx = self.file.createElement("x")
            x_text = self.file.createTextNode(str(players[i].xpos_left))
            wspx.appendChild(x_text)
            gracz.appendChild(wspx)
            wspy = self.file.createElement("y")
            y_text = self.file.createTextNode(str(players[i].ypos_top))
            wspy.appendChild(y_text)
            gracz.appendChild(wspy)
            zn_gracze.appendChild(gracz)
        frame.appendChild(zn_gracze)
        zn_bomby = self.file.createElement("bombs")
        if not len(obiekty) == 0:
            for i in obiekty:
                bomba = self.file.createElement("bomb")
                bomba.setAttribute("x", str(i.posx_left))
                bomba.setAttribute("y", str(i.posy_top))
                text = self.file.createTextNode(str(i.explode))
                bomba.appendChild(text)
                zn_bomby.appendChild(bomba)
        frame.appendChild(zn_bomby)
        self.file.childNodes[0].appendChild(frame)

    def load_replay(self, path):
        wyjscie = []
        frame_counter = 0
        file = minidom.parse(path)
        frames = file.getElementsByTagName("frame")
        for frame in frames:
            wektor = []
            time = frame.getAttribute("time")
            wektor.append(time)
            frame_counter += 1
            mapa = frame.getElementsByTagName("mapa")
            pola = mapa[0].getElementsByTagName("pole")
            wektor_pole = []
            for pole in pola:
                mapa_x = pole.getAttribute("x")
                mapa_y = pole.getAttribute("y")
                type = self.getText(pole.childNodes)
                wektor_pole.append([mapa_x, mapa_y, type])
            wektor.append(wektor_pole)
            gracze = frame.getElementsByTagName("gracze")
            gracze = gracze[0].getElementsByTagName("gracz")
            wektor_gracz = []
            for gracz in gracze:
                id = gracz.getAttribute("id")
                gracz_x = gracz.getElementsByTagName("x")
                gracz_x = self.getText(gracz_x[0].childNodes)
                gracz_y = gracz.getElementsByTagName("y")
                gracz_y = self.getText(gracz_y[0].childNodes)
                wektor_gracz.append([id, gracz_x, gracz_y])
            wektor.append(wektor_gracz)
            bombs = frame.getElementsByTagName("bombs")
            bombs = bombs[0].getElementsByTagName("bomb")
            wektor_bomb = []
            for bomb in bombs:
                bomb_x = bomb.getAttribute("x")
                bomb_y = bomb.getAttribute("y")
                wektor_bomb.append([bomb_x, bomb_y])
            wektor.append(wektor_bomb)
            wyjscie.append(wektor)
        return wyjscie

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def save_xml(self):
        self.file.writexml(open(self.link, 'w'),
                    indent="",
                    addindent="",
                    newl='\n')
        print("Zapisano powtorke.")