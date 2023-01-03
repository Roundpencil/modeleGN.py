# import json
from PyQt5.QtCore import Qt

from GUIGN import *
from modeleGN import *


# TODO : charger perso
# TODO : sauver perso
# TODO : affiher images
# TODO : supprimer images
# TODO : double clic sur intrigues > ouverture intrigues
# TODO : double clic sur intrigues > ouverture évènement (?)
# TODO : bouton nouvelle intrigue

# qt_creator_file = "mainwindow.ui"
# Ui_MainWindow, _ = uic.loadUiType(qt_creator_file)
# commenté car on ne marche pas comme cela

class ListeEvenementsModel(QtCore.QAbstractListModel):

    def __init__(self, personnage=Personnage(), *args, **kwargs):
        super(ListeEvenementsModel, self).__init__(*args, **kwargs)
        self.evenements = []
        #        if not personnage:
        #            self.personnage = Personnage()
        #        else:
        #            self.personnage = personnage

        for r in personnage.roles:
            for e in r.conteneur.scenes:
                self.evenements.append(e)

            # TODO : trouver comment trier les évènements par date evenements.sort(key=get_date) > sorted(key)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # print("fetching evenements for printing")
            e = self.scenes[index.row()]
            text = "(" + e.date + ") : " + e.pitch + "[" + e.conteneur.nom + "]"
            return text

    def rowCount(self, index):
        return len(self.scenes)


class ListeIntriguesModel(QtCore.QAbstractListModel):
    def __init__(self, personnage=Personnage(), *args, **kwargs):
        super(ListeIntriguesModel, self).__init__(*args, **kwargs)
        self.rolesIntrigues = []
        for r in personnage.roles:
            print("ajout d'un rôle")
            self.rolesIntrigues.append([r, r.conteneur])
            print("rôle ajouté")

    def data(self, index, role):
        # print("fetching d'une data")
        if role == Qt.DisplayRole:
            r, i = self.rolesIntrigues[index.row()]
            text = str(r) + " dans " + str(i)
            print(text)
            return text

    def rowCount(self, index):
        # print("rolintigue appelé ")
        # print(len(self.rolesIntrigues))
        # print(self.rolesIntrigues[0])
        return len(self.rolesIntrigues)


class FenetrePersonnage(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, personnage=None):
        super(FenetrePersonnage, self).__init__()
        if not personnage:
            self.personnage = Personnage()
        else:
            self.personnage = personnage

        self.setupUi(self)
        self.personnage = personnage

        # self.findChild(QtWidgets.QTextEdit, "textNom").setText(personnage.nom)
        # self.findChild(QtWidgets.QTextEdit, "textDriver").setText(personnage.driver)
        # self.findChild(QtWidgets.QTextEdit, "textDescription").setText(personnage.description)
        # self.findChild(QtWidgets.QTextEdit, "textQuestions").setText(personnage.questions_ouvertes)
        #
        # #        self.findChild(QtWidgets.QListView, "listViewIntrigues").model = ListeIntriguesModel(personnage)
        # self.findChild(QtWidgets.QListView, "listViewIntrigues").setModel(ListeIntriguesModel(personnage))
        # self.findChild(QtWidgets.QListView, "listViewEvenements").setModel(ListeEvenementsModel(personnage))

        self.textNom.setText(personnage.nom)
        self.textDriver.setText(personnage.driver)
        self.textDescription.setText(personnage.description)
        self.textQuestions.setText(personnage.questions_ouvertes)

        #        self.findChild(QtWidgets.QListView, "listViewIntrigues").model = ListeIntriguesModel(personnage)
        self.findChild(QtWidgets.QListView, "listViewIntrigues").setModel(ListeIntriguesModel(personnage))
        self.findChild(QtWidgets.QListView, "listViewEvenements").setModel(ListeEvenementsModel(personnage))

        self.boutonAppliquer.pressed.connect(self.enregistrer)

        # self.addButton.pressed.connect(self.add)
        # self.deleteButton.pressed.connect(self.delete)
        # self.completeButton.pressed.connect(self.complete)

        self.accept = True  # test
        # TODO ajouter un double clic sur les listes

    def enregistrer(self):
        self.personnage.nom = self.textNom.toPlainText()
        self.personnage.driver = self.textDriver.toPlainText()
        self.personnage.description = self.textDescription.toPlainText()
        self.personnage.questions_ouvertes = self.textQuestions.toPlainText()
