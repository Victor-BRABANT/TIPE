from tkinter import *
from random import *
from time import *

haut = 2			# Nombre de lignes de la route
larg = 100			# Nombre de colonnes de la route
cote = 10 			# Taille d'une cellule (en px)
marge_haut = 30 	# Espacement entre les bords hauts et bas de l'écran et le tableau (en px)
marge_cote = 30 	# Espacement entre les bords droits et gauches de l'écran et le tableau (en px)

mv_to_mv = 0.9		# Probabilité d'avancer si le véhicule est déjà en mouvement
mv_to_ar = 0.1 		# Probabilité de s'arrêter si le véhicule est déjà en mouvement
ar_to_mv = 0.3 		# Probabilité d'avancer si le véhicule est à l'arrêt
ar_to_ar = 0.7 		# Probabilité de s'arrêter si le véhicule est à l'arrêt

tmp_acc = 10 		# Temps de disparition d'un accident (en nombre de tours)

spawn = 0.7  		# Probabilité qu'un véhicule apparaisse sur la première case

vitesse_anim = 1500	# Actualisation de l'animation (en ms)


"""
Faire en sorte que si une voiture veut doubler et donc se déplacer en diagonale elle ne puisse pas
le faire si une voiture se trouve sur une case de "passage" pour aller sur la diagonale
"""


class voiture(object):
	"""
	un maillon voiture

	Attributs :
		- type  : Indique que c'est un objet voiture
		- x 	: La position x de la voiture sur la route
		- y 	: La position y de la voiture sur la route
		- mvt 	: Un booléen indiquant si la voiture est en mouvement ou non
		- dirx 	: La direction en x de la voiture (-1 à gauche, 0 rien, 1 à droite)
		- diry	: La directino en y de la voiture (-1 en haut, 0 rien, 1 en bas)
		- pred	: La voiture précédente dans la liste des voitures sur la route
		- suiv 	: La voiture suivante dans la liste des voitures sur la route
	"""

	def __init__(self, pred, suiv, x, y, mvt, dirx, diry):
		self.type = "V"
		self.x = x
		self.y = y
		self.mvt = mvt
		self.dirx = dirx
		self.diry = diry
		self.pred = pred
		self.suiv = suiv

	def taille(self):
		"""
		Renvoi le nombre de voitures restantes dans la liste en se comptant
		"""
		if self.suiv == None:
			return 1
		else:
			return 1 + taille(self.suiv)

	def pivoter(self, dirx, diry):
		self.dirx = dirx
		self.diry = diry
		return self

	def pivot45D(self):
		dx = self.dirx
		dy = self.diry
		ndx = 0
		ndy = 0
		if dx == 1:
			if dy == 1:
				ndx = 0
				ndy = 1
			else:
				ndx = dx
				ndy = dy+1
		elif dx == 0:
			ndx = -1*dy
			ndy = dy
		else:
			if dy == -1:
				ndx = 0
				ndy = -1
			else:
				ndx = dx
				ndy = dy-1
		self.dirx = ndx
		self.diry = ndy
		return self

	def pivot90D(self):
		self.pivot45D()
		self.pivot45D()
		return self

	def pivot135D(self):
		self.pivot90D()
		self.pivot45D()
		return self

	def pivot180(self):
		self.dirx = -(self.dirx)
		self.diry = -(self.diry)
		return self

	def pivot45G(self):
		self.pivot180()
		self.pivot90D()
		self.pivot45D()
		return self

	def pivot90G(self):
		self.pivot180()
		self.pivot90D()
		return self

	def pivot135G(self):
		self.pivot180()
		self.pivot45D()
		return self

class voitures(object):
	"""
	Liste chaînée des voitures

	Attribut :
		- tete 	: La première voiture de la liste
	"""

	def __init__(self):
		self.tete = None	# Symbolise la liste vide

	def est_vide(self):
		"""
		Renvoi true si la liste des voitures est vide, false sinon
		"""
		return self.tete == None

	def taille(self):
		"""
		Renvoi la taille de la liste des voitures
		"""
		if self.tete == None:
			return 0
		else:
			return self.tete.taille()

	def ajouter(self, x, y, mvt, dirx, diry):
		"""
		Ajoute une voiture à la liste des voitures 
		"""
		m = voiture(None, self.tete, x, y, mvt, dirx, diry)
		if self.tete != None:
			self.tete.pred = m
		self.tete = m
		return m

	def retirer(self, voit):
		"""
		Retire le maillon voit de la liste chaînée
		"""
		if not self.est_vide() and voit != None:
			if voit.suiv != None:
				voit.suiv.pred = voit.pred
			if voit.pred != None:
				voit.pred.suiv = voit.suiv
			if voit.x == self.tete.x and voit.y == self.tete.y:
				self.tete = voit.suiv


class accident(object):
	"""
	un maillon accident

	Attributs :
		- type 	: Indique que l'objet est un accident
		- x 	: La position x de l'accident sur la route
		- y 	: La position y de l'accident sur la route
		- t 	: La durée restante avant la disparition de l'accident
		- pred	: L'accident précédent dans la liste des accidents sur la route
		- suiv 	: L'accident suivant dans la liste des accidents sur la route
	"""

	def __init__(self, pred, suiv, x, y, t):
		self.type = "A"
		self.x = x
		self.y = y
		self.t = t
		self.pred = pred
		self.suiv = suiv

	def taille(self):
		"""
		Renvoi le nombre d'accident restant dans la liste en se comptant
		"""
		if self.suiv == None:
			return 1
		else:
			return 1 + taille(self.suiv)

class accidents(object):
	"""
	Liste chaînée des accidents

	Attribut :
		- tete 	: Le premier accident de la liste
	"""

	def __init__(self):
		self.tete = None	# Symbolise la liste vide

	def est_vide(self):
		"""
		Renvoi true si la liste des accidents est vide, false sinon
		"""
		self.tete == None

	def taille(self):
		"""
		Renvoi la taille de la liste des accidents
		"""
		if self.tete == None:
			return 0
		else:
			return self.tete.taille()

	def ajouter(self, x, y, t):
		"""
		Ajoute un accident à la liste des accidents
		"""
		m = accident(None, self.tete, x, y, t)
		if self.tete != None:
			self.tete.pred = m
		self.tete = m
		return m

	def retirer(self, acc):
		"""
		Retire le maillon acc de la liste chaînée
		"""
		if not self.est_vide() and acc != None:
			if acc.suiv != None:
				acc.suiv.pred = acc.pred
			if acc.pred != None:
				acc.pred.suiv = acc.suiv
			if acc.x == self.tete.x and acc.y == self.tete.y:
				self.tete = acc.suiv


class Case(object):
	"""
	Représentation graphique d'une case de la matrice

	Attributs :
		- x 		 : Coordonnée d'abscisse
		- y    		 : Coordonnée d'ordonnée
		- dirx 		 : Le sens de circulation en x de la route (-1 : G, 0 : R, 1 : D)
		- diry		 : Le sens de circulation en y de la route (-1 : H, 0 : R, 1 : B)
		- cote 	 	 : Taille d'une cellule (en px)
		- marge_haut : Espacement bord/tableau haut/bas (en px)
		- marge_cote : Espacement bord/tableau droite/gauche (en px)
		- canvas 	 : Interface graphique
		- visu 	 	 : Représentation graphique de la cellule
	"""

	def __init__(self, x, y, dirx, diry, cote, marge_haut, marge_cote, canvas):
		self.x = x
		self.y = y
		self.dirx = dirx
		self.diry = diry
		self.cote = cote
		self.marge_haut = marge_haut
		self.marge_cote = marge_cote
		self.canvas = canvas
		self.visu = self.create_cell()


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

	def affiche_vehicule(self, etat):
		"""
		Change la couleur de la cellule en fonction de l'état du véhicule
		"""
		color = "red"
		if etat[self.y][self.x].type == "A":
			color = "black"
		elif etat[self.y][self.x].type == "V":
			if etat[self.y][self.x].mvt:
				color = "blue"
		self.canvas.itemconfig(self.visu, fill = color)

	def cache_vehicule(self):
		"""
		"Retire" le véhicule de la cellule
		"""
		self.canvas.itemconfig(self.visu, fill = "white")

	def actualise_visu(self, etat):
		"""
		Actualise l'apparence graphique de la cellule en fonction de son état
		"""
		if etat[self.y][self.x] != None :
			self.affiche_vehicule(etat)
		else :
			self.cache_vehicule()


class Route(object):
	"""
	La matrice des Case

	Attributs :
		- canvas 	 : Gère l'affichage graphique
		- haut 		 : nombre de lignes de cellules
		- larg 		 : nombre de colonnes de cellules
		- cote		 : taille d'une cellule (en px)
		- marge_haut : espacement bord/tableau haut/bas (en px)
		- marge_cote : espacement bord/tableau droite/gauche (en px)
		- route      : matrice contenant les visuels des cellules
		- etat       : matrice contenant l'état des cases, None ou un objet voiture
		- voitures 	 : liste des voitures sur la route
		- voits_temp : 2e liste permettant de pré-calculer l'état suivant
		- voits_del	 : liste des visuels à retirer de la route à l'état suivant
		- accidents  : liste des accidents sur la route
	"""

	def __init__(self, haut, larg, cote, marge_haut, marge_cote, fen):
		self.canvas = Canvas(fen, width=(larg*cote)+marge_cote, height=(haut*cote)+marge_haut, highlightthickness=0)
		self.haut = haut
		self.larg = larg
		self.cote = cote
		self.marge_haut = marge_haut
		self.marge_cote = marge_cote
		self.route = [
			[Case(col, row, 1, 0, cote, marge_haut, marge_cote, self.canvas) for col in range(larg)] 
				for row in range(haut)]
		self.etat = [
			[None for col in range(larg)]
				for row in range(haut)]
		self.voitures = voitures()
		self.voits_temp = voitures()
		self.voits_del = voitures()
		self.accidents = accidents()

		self.canvas.pack()
	
	def front_libre(self, voit):
		"""
		Renvoi true si le véhicule en x y peut aller sur la case en face de lui, false sinon.
		Le véhicule peut se déplacer sur la case si elle est vide ou si
		un autre véhicule l'occupe mais que ce véhicule est en mouvement.
		"""

		x = voit.x
		y = voit.y
		if (0 <= x+voit.dirx and x+voit.dirx < self.larg):
			if (0 <= y+voit.diry and y+voit.diry < self.haut):
				front_case = self.etat[y+voit.diry][x+voit.dirx]
				present = front_case != None
				if present:
					if front_case.type == "A": 
						return False
					elif front_case.type == "V":
						if not front_case.mvt:
							return False
						elif front_case.x + front_case.dirx == x and front_case.y + front_case.diry == y:
							return False
						else:
							return True
				return True
		return False


	def deplace(self, voit):
		"""
		Fais avancer le véhicule selon les possibilités qu'il a,
		soit il avance dans sa direction
		soit il change de voie pour doubler
		soit il s'arrête

		à noter : La voie de droite se situe en bas
		"""
		x = voit.x
		y = voit.y
		dx = voit.dirx
		dy = voit.diry
		if 0 <= x+dx and x+dx < self.larg:					# Si le véhicule n'est pas au bout
			if 0 <= y+dy and y+dy < self.haut:
				if self.front_libre(voit.pivot45D()):		# Si il peut se rabatre
					self.voits_temp.ajouter(x+voit.dirx, y+voit.diry, True, dx, dy)
				elif self.front_libre(voit.pivoter(dx, dy)):	# Si il peut avancer
					self.voits_temp.ajouter(x+dx, y+dy, True, dx, dy)	
				elif self.front_libre(voit.pivot45G()):		# Si il peut doubler
					self.voits_temp.ajouter(x+voit.dirx, y+voit.diry, True, dx, dy)
				else:
					self.voits_temp.ajouter(x, y, False, dx, dy)
		voit.pivoter(dx, dy)
		self.voits_del.ajouter(x,y,False,dx,dy)

	def copie(self):
		"""
		Met à jour les listes originales des voitures et accidents sur la route 
		ainsi que la matrice état
		"""

		while self.voits_del.tete != None:	
			# On retire visuellement les anciennes positions des voitures
			cell_t = self.voits_del.tete
			self.route[cell_t.y][cell_t.x].cache_vehicule()
			self.etat[cell_t.y][cell_t.x] = None
			self.voits_del.retirer(cell_t)

		cell = voitures()

		while self.voits_temp.tete != None:
			# On met à jour les nouvelles positions des voitures en notant les accidents
			cell_t = self.voits_temp.tete
			if self.etat[cell_t.y][cell_t.x] != None:
				# Accident
				cell.retirer(self.etat[cell_t.y][cell_t.x])
				a = self.accidents.ajouter(cell_t.x, cell_t.y, tmp_acc)
				self.etat[cell_t.y][cell_t.x] = a
			else:
				c = cell.ajouter(cell_t.x, cell_t.y, cell_t.mvt, cell_t.dirx, cell_t.diry)
				self.etat[cell_t.y][cell_t.x] = c
			self.route[cell_t.y][cell_t.x].actualise_visu(self.etat)
			self.voits_temp.retirer(cell_t)

		cell_a = accidents()
		while self.accidents.tete != None:
			# On met à jour les accidents en diminuant de 1 leur temps d'apparition
			cell_t = self.accidents.tete
			if cell_t.t > 0:
				a = cell_a.ajouter(cell_t.x, cell_t.y, cell_t.t-1)
				self.etat[cell_t.y][cell_t.x] = a
				self.route[cell_t.y][cell_t.x].actualise_visu(self.etat)
			else:
				self.route[cell_t.y][cell_t.x].cache_vehicule()
				self.etat[cell_t.y][cell_t.x] = None
			self.accidents.retirer(cell_t)


		self.voitures = cell
		self.accidents = cell_a


	def reset_temp(self):
		"""
		Reinitialise la liste secondaire des voitures
		"""

		self.voits_temp = voitures()


	def choix_initial(self, voit):
		"""
		Renvoi true si le prochain état du véhicule est d'avancer
		false si il est de s'arrêter selon la loi définit au début
		"""

		r = randint(1, 100)
		if voit.mvt:
			if r <= (mv_to_mv*100):
				return True
			else:
				return False
		elif r <= (ar_to_mv*100):
			return True
		else:
			return False

	def etat_suiv(self, voit):
		"""
		Calcul et effectue l'état suivant du véhicule en x y
		"""

		
		if self.choix_initial(voit):
			self.deplace(voit)
		else:
			self.voits_temp.ajouter(voit.x, voit.y, False, voit.dirx, voit.diry)
			self.voits_del.ajouter(voit.x, voit.y, False, voit.dirx, voit.diry)
	
	def inserer(self):
		"""
		Insère un véhicule au début (0, 0)
		"""
		self.voits_temp.ajouter(0,1,True,1,0)

	def nait(self):
		"""
		Fait apparaître aléatoirement un véhicule au début si possible
		"""

		if self.etat[0][0] == None:
			r = randint(1, 100)
			if r <= (spawn*100):
				self.inserer()


	def vie(self):
		"""
		Fait vivre la matrice
		"""

		self.nait()					# On fait apparaître un véhicule si le hasard le veut
		cell = self.voitures.tete
		while cell != None:
			# On actualise toutes les voitures présentes sur la route
			self.etat_suiv(cell)
			cell = cell.suiv

		
		self.copie()				# Copie des listes temporaires dans les originales
		self.reset_temp()			# Réinitialisation des listes temporaires
		fen.after(vitesse_anim, self.vie)


fen = Tk()
fen.title("Simulation traffic")

route = Route(haut, larg, cote, marge_haut, marge_cote, fen)
#fen.attributes("-fullscreen", True)
route.vie()

fen.mainloop()