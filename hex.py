import os
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

	def __init__(self, display, number_of_hexagons, xoffset, mark_action):
		self.display = display
		self.number_of_hexagons = number_of_hexagons
		self.rect_width = LONG*number_of_hexagons*1.421
		self.rect_height = LONG*number_of_hexagons+1
		self.xoffset = 2*self.rect_width + xoffset
		self.id_limit = 0
		self.mark_action = mark_action
		self.start()
		
	def start(self):
		self.hexagons = {}
		self.id = 0
		# start suspension of a player from playing once he gets a question until the question is answered correctly or the timer expires
		self.l_player_suspend, self.r_player_suspend = False, False
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
		if x > self.xoffset and (not self.r_player_suspend):
			rclick = True
		elif x <= self.xoffset and (not self.l_player_suspend):
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
					self.mark_action(hl)
					won = self.solve(hl.id)
				if rr:
					#print("Processing rr event")
					hl.color = hr.color
					hl.marked = hr.marked
					self.mark_action(hr)
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
	def __init__(self, duration, step, update_action, expiry_action, start_time):
		self.duration = duration
		self.step = step
		self.update_action = update_action
		self.expiry_action = expiry_action
		self.start_time = start_time
		
	def format_time(self, time_s):
		return "{:03d}:{:02d}".format(time_s//60, time_s%60)
	
	def __str__(self):
		return self.format_time(self.duration)

	def update(self, current_time):
		if self.duration <= 0:
			self.expiry_action()
			return False
		elif (abs(current_time - self.start_time) >= self.step):
			start_time = current_time
			self.update_action(self)
			self.duration -= self.step
			return True
		return True
	
class display:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Pravega Hex")
		icon = pygame.image.load("dna-icon.png")
		pygame.display.set_icon(icon)
		self.clock = pygame.time.Clock()
		self.number_of_hexagons = 6
		# os.environ["SDL_VIDEO_CENTERED"] = "1"
		self.width = LONG*54
		self.height = LONG*self.number_of_hexagons*3
		self.display = pygame.display.set_mode((self.width, self.height))
		self.won = True
		self.color = None
		self.xoffset = 560
		self.table = Table(self.display, self.number_of_hexagons, self.xoffset, self.mark_action)
		self.font = Font()
		self.text_width = 0
		self.timers = []
		# <timer_test>
		self.timer_text_loc = (200, 2*self.table.rect_height+((self.height-2*self.table.rect_width)//2))
		self.add_timer(Timer(10, 1, self.handleTimerEvent, self.handleTimerExpiry, time.clock())) #for testing only
		# </timer_test>
		self.display.fill(WHITE)
		self.main()		   

	def add_timer(self, timer):
		self.timers.append(timer)
		self.set_timer()
	
	def set_timer(self):
		pygame.time.set_timer(TICK_EVENT, self.min_sleep()*1000)
		
	def min_sleep(self):
		return min([self.timers[i].step for i in range(len(self.timers))])
		
	def mark_action(self, hexagon):
		# do something here if a cell is marked
		pass

	def min(sequence):
		low = sequence[0]
		for i in sequence:
			if i < low:
				low = i
		return low

	def draw_text(self, raw_text, text_loc):
		tmp_size = self.font.font.size(raw_text)
		if tmp_size[0] > self.text_width:
			self.text_width = tmp_size[0]
		size = (self.text_width, tmp_size[1])
		timer_text = self.font.render(raw_text)
		self.display.fill(WHITE, (text_loc[0], text_loc[1], size[0], size[1]))
		self.display.blit(timer_text, text_loc)
		pygame.display.update()
		
	def handleTimerEvent(self, timer):
		self.draw_text(str(timer), self.timer_text_loc)
	
	def handleTimerExpiry(self):
		self.draw_text("Timer Expired", self.timer_text_loc)
	
	def main(self):
		global RUN
		while RUN:
			self.display.fill(WHITE, (0, 0, 4*self.table.rect_width+self.xoffset, 2*(self.table.rect_height+1)))
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
					if not timer.update(time.clock()):
						timers_bk.remove(timer)
				self.timers = timers_bk
			if event.type == pygame.QUIT:
				return False
		return True

display()