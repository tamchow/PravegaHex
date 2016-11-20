# import os
import random
from threading import Thread
import pygame

# constants
RUN = True
LONG = 40
YELLOW = (255, 231, 0)
FOCUS_COLOR = (50,125,50)
BLUE = (0, 127, 245)
WHITE = (255,255,255)
BLACK = (0,0,0)
LEFT = 1
RIGHT = 3
COLOR_PLAYER_CLEAR = FOCUS_COLOR
player = random.choice((BLUE, YELLOW))

def check_player(lp, rp):
	global player
	
	if rp:
		player = YELLOW
	elif lp:
		player = BLUE
		

class Font:

	def __init__(self):
		pygame.font.init()
		self.font = pygame.font.Font("cubicfive10.ttf", 20)

	def render(self, text):
		return self.font.render(text, False, BLACK)


class Hexagon:

	def __init__(self, display, x, y, id, blue_start, blue_end, yellow_start, yellow_end):
		self.display = display
		self.d = LONG
		self.color = WHITE
		self.marked = False
		self.id = id
		self.blue_start = blue_start
		self.blue_end = blue_end
		self.yellow_start = yellow_start
		self.yellow_end = yellow_end
		# coordinates of centre
		self.x = x
		self.y = y
		#self.rendered_id = Font().render(str(id))
		self.rect = pygame.Rect(self.x - self.d/2 - 4, self.y - self.d, self.d + 8, self.d*2)

	def draw(self):
		pl = [(self.x - self.d, self.y),
			  (self.x - self.d/2, self.y - self.d),
			  (self.x + self.d/2, self.y - self.d),
			  (self.x + self.d, self.y),
			  (self.x + self.d/2, self.y + self.d),
			  (self.x - self.d/2, self.y + self.d)]
		pygame.draw.polygon(self.display, self.color, pl)
		pygame.draw.polygon(self.display, (100,100,100), pl, 3)
		#self.display.blit(self.rendered_id,(self.x,self.y))

	def update(self, x, y, lp, rp):
		c = self.rect.collidepoint(x, y)
		if c:
			if (lp or rp) and self.color == COLOR_PLAYER_CLEAR:
				check_player(lp, rp)
				self.mark()
				return 1
			return 2
		return 0
		
	def mark(self):
		self.color = player
		self.marked = True
			
	def focus(self):
		if not self.marked:
			self.color = COLOR_PLAYER_CLEAR
		
	def defocus(self):
		if not self.marked:
			self.color = WHITE


class Table:

	def __init__(self, display, number_of_hexagons, xoffset):
		self.display = display
		self.number_of_hexagons = number_of_hexagons
		self.xoffset = xoffset
		self.id_limit = 0
		self.start()
		
	def start(self):
		self.hexagons = {}
		self.focus = None
		self.id = 0
		dx = LONG
		dy = LONG*self.number_of_hexagons
		# Table
		for i in range(self.number_of_hexagons):
			for e in range(self.number_of_hexagons):
				x = dx + LONG*(e + i)*1.5
				y = dy + LONG*(i - e)
				self.id += 1
				blue_start, blue_end, yellow_start, yellow_end = self.edge(self.id)
				self.hexagons[self.id] = Hexagon(self.display, x, y, self.id, blue_start, blue_end, yellow_start, yellow_end)
		self.id_limit = self.id	- 1
		for i in range(self.number_of_hexagons):
			for e in range(self.number_of_hexagons):
				x = dx + LONG*(e + i)*1.5 + self.xoffset
				y = dy + LONG*(i - e)
				self.id += 1
				blue_start, blue_end, yellow_start, yellow_end = self.edge(self.id)
				self.hexagons[self.id] = Hexagon(self.display, x, y, self.id, blue_start, blue_end, yellow_start, yellow_end)
				
	def edge(self, id):
		# corner <
		if id == 1:
			return True, False, True, False
		# corner ^
		elif id == self.number_of_hexagons:
			return False, True, True, False
		# corner v
		elif id == self.number_of_hexagons*(self.number_of_hexagons-1)+1:
			return True, False, False, True
		# corner >
		elif id == self.number_of_hexagons**2:
			return False, True, False, True
		# edge <v blue_start
		elif id % self.number_of_hexagons == 1:
			return True, False, False, False
		# edge <^ yellow_start
		elif id > 1 and id < self.number_of_hexagons:
			return False, False, True, False
		# edge ^> blue_end		
		elif id % self.number_of_hexagons == 0:
			return False, True, False, False
		# edge v> yellow_end
		elif (id - self.number_of_hexagons*(self.number_of_hexagons-1)) > 1 and (id - self.number_of_hexagons*(self.number_of_hexagons-1)) < self.number_of_hexagons:
			return False, False, False, True
		# internal
		else:
			return False, False, False, False

	def draw(self):
		xoffset = self.xoffset
		pygame.draw.rect(self.display, YELLOW, (0, 0, LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons))
		pygame.draw.rect(self.display, BLUE, (LONG*self.number_of_hexagons*1.5, 0, LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons))
		pygame.draw.rect(self.display, BLUE, (0, LONG*self.number_of_hexagons, LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons))
		pygame.draw.rect(self.display, YELLOW, (LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons, LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons))	
		
		pygame.draw.rect(self.display, YELLOW, (xoffset, 0, LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons))
		pygame.draw.rect(self.display, BLUE, ((LONG*self.number_of_hexagons*1.5) + xoffset, 0, LONG*self.number_of_hexagons*1.5, LONG*self.number_of_hexagons))
		pygame.draw.rect(self.display, BLUE, (xoffset, LONG*self.number_of_hexagons, (LONG*self.number_of_hexagons*1.5), LONG*self.number_of_hexagons))
		pygame.draw.rect(self.display, YELLOW, ((LONG*self.number_of_hexagons*1.5)+xoffset, LONG*self.number_of_hexagons, (LONG*self.number_of_hexagons*1.5), LONG*self.number_of_hexagons))
		x, y = pygame.mouse.get_pos()		 
		# event = pygame.event.wait()
		lclick, rclick = False, False
		# if(event.type == pygame.MOUSEBUTTONDOWN):
			# lclick, rclick = (event.button == LEFT), (event.button == RIGHT)
		if(x>xoffset):
			rclick = True
		elif(x<=xoffset):
			lclick = True
		won = None
		mod_hexagons = {}
		#print(self.hexagons)
		for id, hexagon in self.hexagons.items():
			hexagon_right = self.hexagons[self.id_limit+id]
			if(id>self.id_limit):
				break
			else:
				if hexagon.marked:
					print("Adding LHex\n")
					mod_hexagons[id] = hexagon
				elif hexagon_right.marked:
					print("Adding RHex\n")
					mod_hexagons[id] = hexagon_right
				elif ((not hexagon.marked) and (not hexagon_right.marked)):
					mod_hexagons[id] = hexagon
		#self.hexagons = mod_hexagons
		#print(mod_hexagons)
		for hl in self.hexagons.values():
			#hr = Hexagon(hl.display, hl.x+self.xoffset, hl.y, hl.id, hl.blue_start, hl.blue_end, hl.yellow_start, hl.yellow_end)
			rl = hl.update(x, y, lclick, rclick)
			if rl:
				# mark
				if rl == 1:
					self.focus = None
					won = self.solve(hl.id)
				# focus
				elif rl == 2:
					if self.focus and self.focus != hl:
						self.focus.defocus()
					self.focus = hl
			if self.focus:
				self.focus.focus()
			
			hl.draw()
			#hr.draw()
		return won
			
	def solve(self, id):
		seen = []
		color = self.hexagons[id].color
		chain = [h for h in self.around(id, color, seen)]
		if self.beginning(chain, color) and self.end(chain, color):
			return color
		return None
		
	def around(self, id, color, seen):
		# Returns the ids of the Hexagons of the same color around one
		if self.edge(id)[0] == True:
			pos = 0, -(self.number_of_hexagons-1), -self.number_of_hexagons, 1, self.number_of_hexagons
		elif self.edge(id)[1] == True:
			pos = 0, -self.number_of_hexagons, -1, self.number_of_hexagons, (self.number_of_hexagons-1)
		else:
			pos = 0, -(self.number_of_hexagons-1), -self.number_of_hexagons, 1, -1, self.number_of_hexagons, (self.number_of_hexagons-1)
		around = [self.hexagons[id+i].id for i in pos if (((id+i) in self.hexagons) and (id+i not in seen))]
		chain = [self.hexagons[h].id for h in around if (self.hexagons[h].color == color)]
		seen.extend(chain)
		for i in chain:
			self.around(i, color, seen)
		return seen

	def beginning(self, chain, color):
		if color == BLUE:
			for c in chain:
				if self.hexagons[c].blue_start:
					return True
		else:
			for c in chain:
				if self.hexagons[c].yellow_start:
					return True			   
		return False
	
	def end(self, chain, color):
		if color == BLUE:
			for c in chain:
				if self.hexagons[c].blue_end:
					return True
		else:
			for c in chain:
				if self.hexagons[c].yellow_end:
					return True			   
		return False
	
# class CountDownTimer:
	# def __init__(self, display, duration_s, step_s, x, y, width, height, back_color, fore_color):
		# self.display = display
		# self.duration_s = duration_s
		# self.step_s = step_s
		# self.x = x
		# self.y = y
		# self.width = width
		# self.height = height
		# self.back_color = back_color
		# self.fore_color = fore_color
		# self.time_s = duration_s
	
	# def format_mm_ss(time_s):
		# return str(time_s/60+":"+time_s%60)
	
	# def draw(self):
		# disp_time = self.format_mm_ss(self.time_s)
		# pygame.draw.rect()
		
	# def update(self):
		# self.draw()
		# if(self.time_s == 0):
			# return True
		# else:
			# self.time_s -= step_s
			# return False
			

class display:

	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Hex")
		self.clock = pygame.time.Clock()
		self.number_of_hexagons = 6
		# os.environ["SDL_VIDEO_CENTERED"] = "1"
		self.display = pygame.display.set_mode((LONG*64, LONG*self.number_of_hexagons*3))
		self.won = True
		self.color = None
		self.xoffset = 1000
		self.table = Table(self.display, self.number_of_hexagons, self.xoffset)
		self.font = Font()
		self.main()		   

	def main(self):
		global RUN
		while RUN:
			self.display.fill(FOCUS_COLOR)
			# display			
			pygame.event.pump()
			if not self.won:
				color = self.table.draw()
				if color:
					self.won = True
					self.color = color
			else:
				self.winner()
			pygame.display.update()
			if not self.update():
				RUN = False
				break
			self.clock.tick(15)
		pygame.display.quit()
		pygame.quit()
		quit()
		
	def winner(self):
		if self.color == BLUE:
			color = "blue"
		else:
			color = "yellow"

		if self.color:
			r1 = self.font.render(color + " player won!")
		r2 = self.font.render("[i] Start")
		r3 = self.font.render("[Esc] Exit")
		
		if self.color:
			self.display.blit(r1, (200,50))
		self.display.blit(r2, (200,200))
		self.display.blit(r3, (200,250))

	def update(self):
		pressed_key = pygame.key.get_pressed()
		if pressed_key[pygame.K_ESCAPE]:
			return False
		elif pressed_key[pygame.K_i]:
			self.won = False
			self.table.start()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
		return True

display()