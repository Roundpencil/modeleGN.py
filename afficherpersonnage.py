import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from personnage_controller import *


testPerso = Personnage(nom="Jean", concept="Vengeur", driver="Se venger", description="beau",
                       questions_ouvertes="aucune", sexe="m", pj=True)

monGN = GN()
#gn.personnages().add(testPerso)
monGN.addperso(testPerso)
#gn.save("c:"\testsave.io")

testIntrigue = Intrigue(description="intrigue de test")


testRole = Role(testIntrigue, testPerso, nom="le rôle de test", description="descsirp", pipi=1, pipr=5)

testScene = Scene(testIntrigue, "hier", "blessure")

testIntrigue.scenes.add(testScene)

#testIntrigue.roles().add(testRole)

testPerso.ajouter_role(testRole)

# for r in testPerso.roles:
#     for e in r.intrigue.evenements:
#         text = "(" + e.date + ") : " + e.pitch + "[" + e.intrigue.nom + "]"
#         print(text)

app = QtWidgets.QApplication(sys.argv)
window = FenetrePersonnage(testPerso)
window.show()
app.exec_()