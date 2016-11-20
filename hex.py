# import os
import random
import time
from threading import Thread
import pygame
from pygame.locals import USEREVENT

# constants
RUN = True
LONG = 40
YELLOW = (255, 231, 0)
BLUE = (0, 127, 245)
WHITE = (255,255,255)
BLACK = (0,0,0)
LEFT = 1
RIGHT = 3
TICK_EVENT = USEREVENT+1
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
		self.rendered_id = Font().render(str(id))
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
		self.display.blit(self.rendered_id,(self.x,self.y))

	def update(self, x, y, lp, rp):
		c = self.rect.collidepoint(x, y)
		if c and (lp or rp)  and (not self.marked) and self.color == WHITE:
				check_player(lp, rp)
				self.mark()
				return True
		return False
		
	def mark(self):
		self.color = player
		self.marked = True


class Table:

	def __init__(self, display, number_of_hexagons, xoffset):
		self.display = display
		self.number_of_hexagons = number_of_hexagons
		self.rect_width = LONG*number_of_hexagons*1.42
		self.rect_height = LONG*number_of_hexagons
		self.xoffset = 2*self.rect_width + xoffset
		self.id_limit = 0
		self.start()
		
	def start(self):
		self.hexagons = {}
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
		self.id_limit = self.id
		for i in range(self.number_of_hexagons):
			for e in range(self.number_of_hexagons):
				x = dx + LONG*(e + i)*1.5 + self.xoffset
				y = dy + LONG*(i - e)
				self.id += 1
				blue_start, blue_end, yellow_start, yellow_end = self.edge(self.id)
				self.hexagons[self.id] = Hexagon(self.display, x, y, self.id, blue_start, blue_end, yellow_start, yellow_end)
				
	def edge(self, id):
		if id > self.id_limit:
			id = id - self.id_limit
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
		pygame.draw.rect(self.display, YELLOW, (0, 0, self.rect_width, self.rect_height))
		pygame.draw.rect(self.display, BLUE, (self.rect_width, 0, self.rect_width, self.rect_height))
		pygame.draw.rect(self.display, BLUE, (0, self.rect_height, self.rect_width, self.rect_height))
		pygame.draw.rect(self.display, YELLOW, (self.rect_width, self.rect_height, self.rect_width, self.rect_height))
		
		pygame.draw.rect(self.display, YELLOW, (self.xoffset, 0, self.rect_width, self.rect_height))
		pygame.draw.rect(self.display, BLUE, (self.rect_width + self.xoffset, 0, self.rect_width, self.rect_height))
		pygame.draw.rect(self.display, BLUE, (self.xoffset, self.rect_height, self.rect_width, self.rect_height))
		pygame.draw.rect(self.display, YELLOW, (self.rect_width + self.xoffset, self.rect_height, self.rect_width, self.rect_height))
		x, y = pygame.mouse.get_pos()		 
		# event = pygame.event.wait()
		lclick, rclick = False, False
		# if(event.type == pygame.MOUSEBUTTONDOWN):
			# lclick, rclick = (event.button == LEFT), (event.button == RIGHT)
		if x > self.xoffset:
			rclick = True
		elif x <= self.xoffset:
			lclick = True
		won = None
		for (id, hl) in self.hexagons.items():
			if id > self.id_limit:
				hr = self.hexagons[id - self.id_limit]
			else:
				hr = self.hexagons[self.id_limit + id]
			rl = hl.update(x, y, lclick, rclick)
			rr = hr.update(x, y, lclick, rclick)
			if rl or rr:
				if rl:
					#print("Processing rl event")
					hr.color = hl.color
					hr.marked = hl.marked
					won = self.solve(hl.id)
				if rr:
					#print("Processing rr event")
					hl.color = hr.color
					hl.marked = hr.marked
					won = self.solve(hr.id)
			hl.draw()
			hr.draw()
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
			
class Timer:
	def __init__(self, duration, step, update_action, expiry_action):
		self.duration = duration
		self.step = step
		self.update_action = update_action
		self.expiry_action = expiry_action
		
	def format_time(self, time_s):
		return str(str(time_s//60)+":"+str(time_s%60))
	
	def __str__(self):
		return self.format_time(self.duration)

	def update(self):
		if self.duration <= 0:
			self.expiry_action()
			return False
		else:
			self.update_action(self)
			self.duration -= self.step
			return True
	
class display:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Hex")
		self.clock = pygame.time.Clock()
		self.number_of_hexagons = 6
		# os.environ["SDL_VIDEO_CENTERED"] = "1"
		self.width = LONG*64
		self.height = LONG*self.number_of_hexagons*3
		self.display = pygame.display.set_mode((self.width, self.height))
		self.won = True
		self.color = None
		self.xoffset = 400
		self.table = Table(self.display, self.number_of_hexagons, self.xoffset)
		self.font = Font()
		self.timers = [Timer(10, 1, self.handleTimerEvent, self.handleTimerExpiry)]
		self.min_sleep = min([self.timers[i].step for i in range(len(self.timers))])
		pygame.time.set_timer(TICK_EVENT, self.min_sleep*1000)
		self.main()		   

	def min(sequence):
		low = sequence[0]
		for i in sequence:
			if i < low:
				low = i
		return low

	def handleTimerEvent(self, timer):
		timer_text = self.font.render(str(timer))
		self.display.fill(WHITE)
		self.display.blit(timer_text, (200, 2*self.table.rect_height+((self.height-2*self.table.rect_width)//2)))
		pygame.display.update()
	
	def handleTimerExpiry(self):
		timer_text = self.font.render("Timer expired")
		#print("Timer expired")
		self.display.fill(WHITE)
		self.display.blit(timer_text, (200, 2*self.table.rect_height+((self.height-2*self.table.rect_width)//2)))
		pygame.display.update()
	
	def main(self):
		global RUN
		while RUN:
			self.display.fill(WHITE, (0, 0, 4*self.table.rect_width+self.xoffset, 2*self.table.rect_height))
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
			if event.type == TICK_EVENT:
				timers_bk = self.timers.copy()
				for timer in timers_bk:
					if not timer.update():
						timers_bk.remove(timer)
				self.timers = timers_bk
			if event.type == pygame.QUIT:
				return False
		return True

display()