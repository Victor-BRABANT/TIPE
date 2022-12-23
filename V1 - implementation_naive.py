from tkinter import *
from random import *
from time import *

haut = 10 			# Nombre de lignes
larg = 50			# Nombre de colonnes
cote = 35 			# Taille d'une cellule (en px)
marge_haut = 800 	# Espacement entre les bords hauts et bas et le tableau (en px)
marge_cote = 30 	# Espacement entre les bords droits et gauches et le tableau (en px)

mv_to_mv = 0.9		# Probabilité d'avancer si le véhicule est déjà en mouvement
mv_to_ar = 0.1 		# Probabilité de s'arrêter si le véhicule est déjà en mouvement
ar_to_mv = 0.3 		# Probabilité d'avancer si le véhicule est à l'arrêt
ar_to_ar = 0.7 		# Probabilité de s'arrêter si le véhicule est à l'arrêt

spawn = 0.7  		# Probabilité qu'un véhicule apparaisse sur la première case

vitesse_anim = 1	# Actualisation de l'animation (en ms)


class Case(object):
	"""
	Case du tableau

	Attributs :
		- x 		 : coordonnée d'abscisse
		- y    		 : coordonnée d'ordonnée
		- cote 	 	 : taille d'une cellule (en px)
		- marge_haut : espacement bord/tableau haut/bas (en px)
		- marge_cote : espacement bord/tableau droite/gauche (en px)
		- canvas 	 : interface graphique
		- visu 	 	 : représentation graphique de la cellule
		- pres 	 	 : booléen indiquant si une voiture occupe la case
		- mvt  	 	 : booléen indiquant si la voiture occupant la case est en mouvement
	"""

	def __init__(self, x, y, cote, marge_haut, marge_cote, canvas):
		self.x = x
		self.y = y
		self.cote = cote
		self.marge_haut = marge_haut
		self.marge_cote = marge_cote
		self.canvas = canvas
		self.visu = self.create_cell()
		self.pres = False
		self.mvt = False


	# INTERFACE GRAPHIQUE
	def create_cell(self):
		"""
		Créée une cellule visuelle
		"""

		x = self.x
		y = self.y
		x1 = (x*self.cote) + (self.marge_cote/2)
		y1 = (y*self.cote) + (self.marge_haut/2)
		x2 = ((x+1)*self.cote) + (self.marge_cote/2)
		y2 = ((y+1)*self.cote) + (self.marge_haut/2)
		coords = (x1, y1, x2, y2)
		cell = self.canvas.create_rectangle(coords, outline = "black", width = 1, fill = "white")
		return cell

	def affiche_vehicule(self):
		color = "red"
		if self.mvt:
			color = "blue"
		self.canvas.itemconfig(self.visu, fill = color)

	def cache_vehicule(self):
		self.canvas.itemconfig(self.visu, fill = "white")

	def actualise_visu(self):
		if self.pres :
			self.affiche_vehicule()
		else :
			self.cache_vehicule()




class Route(object):
	"""
	Tableau de cases

	Attributs :
		- canvas 	 : Gère l'affichage graphique
		- haut 		 : nombre de lignes de cellules
		- larg 		 : nombre de colonnes de cellules
		- cote		 : taille d'une cellule (en px)
		- marge_haut : espacement bord/tableau haut/bas (en px)
		- marge_cote : espacement bord/tableau droite/gauche (en px)
		- route      : matrice contenant les visuels des cellules
		- etat       : matrice contenant les cases
		- etat_temp  : 2e matrice permettant de pré-calculer l'état suivant
	"""

	def __init__(self, haut, larg, cote, marge_haut, marge_cote, fen):
		self.canvas = Canvas(fen, width=(larg*cote)+marge_cote, height=(haut*cote)+marge_haut, highlightthickness=0)
		self.haut = haut
		self.larg = larg
		self.cote = cote
		self.marge_haut = marge_haut
		self.marge_cote = marge_cote
		self.etat = [
			[Case(col, row, cote, marge_haut, marge_cote, self.canvas) for row in range(haut)] 
				for col in range(larg)]
		self.etat_temp = [
			[(False, False) for row in range(haut)] 
				for col in range(larg)]

		self.canvas.pack()

	def actualise(self):
		"""
		Actualise l'affichage de la matrice
		"""

		for y in range(self.haut):
			for x in range(self.larg):
				self.etat[x][y].actualise_visu()
	
	def next_libre(self, x, y):
		"""
		Renvoi true si le véhicule en x y peut aller sur la case x+1 y, false sinon
		"""

		if (x+1 < self.larg):
			present = self.etat[x+1][y].pres
			mouvement = self.etat[x+1][y].mvt
			return ((not present) or (present and mouvement))
		return False

	def up_libre(self, x, y):
		"""
		Renvoi true si le véhicule en x y peut aller sur la case x+1 y+1, false sinon
		"""

		if (x+1 < self.larg and y+1 < self.haut):
			present = self.etat[x+1][y+1].pres
			mouvement = self.etat[x+1][y+1].mvt
			return ((not present) or (present and mouvement))
		return False

	def down_libre(self, x, y):
		"""
		Renvoi true si le véhicule en x y peut aller sur la case x+1 y-1, false sinon
		"""

		if (x+1 < self.larg and y-1 >= 0):
			present = self.etat[x+1][y-1].pres
			mouvement = self.etat[x+1][y-1].mvt
			return ((not present) or (present and mouvement))
		return False

	def deplace(self, x, y):
		"""
		Deplace le véhicule en cellule x y sur la cellule x+1 y si possible
		"""
		if self.down_libre(x, y):					# Attention le bas c'est la ligne du haut
			self.etat_temp[x][y] = (False, False)
			self.etat_temp[x+1][y-1] = (True, True)
		elif self.next_libre(x, y):					# On déplace
			self.etat_temp[x][y] = (False, False)	# On retire
			self.etat_temp[x+1][y] = (True, True)	# On place à côté
		elif x+1 == self.larg:
			self.etat_temp[x][y] = (False, False)	# On retire
		elif self.up_libre(x, y):
			self.etat_temp[x][y] = (False, False)	
			self.etat_temp[x+1][y+1] = (True, True)
		else:
			self.etat_temp[x][y] = (True, False)	# On arrête

	def copie(self):
		"""
		Remplace les valeurs de etat par celles calculées pour l'état suivant et stockées
		dans etat_temp
		"""

		for y in range(self.haut):
			for x in range(self.larg):
				self.etat[x][y].pres = self.etat_temp[x][y][0]
				self.etat[x][y].mvt = self.etat_temp[x][y][1]

	def reset_temp(self):
		"""
		Reinitialise la matrice etat_temp
		"""

		self.etat_temp = [
			[(False, False) for row in range(haut)] 
				for col in range(larg)]

	def choix_initial(self, x, y):
		"""
		Renvoi true si le prochain état du véhicule est d'avancer
		false si il est de s'arrêter selon la loi définit au début
		"""

		r = randint(1, 100)
		if self.etat[x][y].mvt:
			if r <= (mv_to_mv*100):
				return True
			else:
				return False
		elif r <= (ar_to_mv*100):
			return True
		else:
			return False

	def etat_suiv(self, x, y):
		"""
		Calcul et effectue l'état suivant du véhicule en x y
		"""

		if self.etat[x][y].pres:
			if self.choix_initial(x, y):
				self.deplace(x, y)
			else:
				self.etat_temp[x][y] = (True, False)
	
	def inserer(self):
		"""
		Insère un véhicule au début (0, 0)
		"""

		self.etat_temp[0][0] = (True, True)

	def nait(self):
		"""
		Fait apparaître aléatoirement un véhicule au début si possible
		"""

		if not self.etat[0][0].pres:
			r = randint(1, 100)
			if r <= (spawn*100):
				self.inserer()


	def vie(self):
		"""
		Fais vivre la matrice
		"""

		self.nait()
		for y in range(self.haut):
			for x in range(self.larg):
				self.etat_suiv(x, y)
		
		self.copie()
		self.reset_temp()
		self.actualise()
		fen.after(vitesse_anim, self.vie)




fen = Tk()
fen.title("Simulation traffic")

route = Route(haut, larg, cote, marge_haut, marge_cote, fen)
#route.etat_temp[1][0] = (True,False)
#route.etat_temp[2][0] = (True,False)
#route.etat_temp[3][0] = (True,False)
fen.attributes("-fullscreen", True)
route.vie()

fen.mainloop()
