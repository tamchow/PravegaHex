import os
import random
import time
from threading import Thread
import pygame
from pygame.locals import USEREVENT

# constants
RUN = True
LONG = 40
RECTANGLE_WIDTH_SCALE = 1.421
SCREEN_WIDTH_SCALE = 54
RECTANGLE_HEIGHT_SCALE = 1
SCREEN_HEIGHT_SCALE = 3
YELLOW = (255, 231, 0)
BLUE = (0, 127, 245)
WHITE = (255,255,255)
BLACK = (0,0,0)
BORDER_COLOR = (100,100,100)
LEFT = 1
RIGHT = 3
TICK_EVENT = USEREVENT+1
NUMBER_OF_HEXAGONS = 6
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
		# self.rendered_id = Font().render(str(id))
		self.rect = pygame.Rect(self.x - self.d/2 - 4, self.y - self.d, self.d + 8, self.d*2)

	def draw(self):
		pl = [(self.x - self.d, self.y),
			  (self.x - self.d/2, self.y - self.d),
			  (self.x + self.d/2, self.y - self.d),
			  (self.x + self.d, self.y),
			  (self.x + self.d/2, self.y + self.d),
			  (self.x - self.d/2, self.y + self.d)]
		pygame.draw.polygon(self.display, self.color, pl)
		pygame.draw.polygon(self.display, BORDER_COLOR, pl, 3)
		# self.display.blit(self.rendered_id,(self.x,self.y))

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
	
	def unmark(self):
		self.color = WHITE
		self.marked = False

class Table:

	def __init__(self, display, number_of_hexagons, xoffset, mark_action):
		self.display = display
		self.number_of_hexagons = number_of_hexagons
		self.rect_width = LONG*number_of_hexagons*RECTANGLE_WIDTH_SCALE
		self.rect_height = (LONG*number_of_hexagons+1)*RECTANGLE_HEIGHT_SCALE
		self.xoffset = 2*self.rect_width + xoffset
		self.id_limit = 0
		# start suspension of a player from playing once he gets a question until the question is answered correctly or the timer expires
		self.l_player_suspend, self.r_player_suspend = False, False
		self.mark_action = mark_action
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
					self.mark_action(hl)
					hr.color = hl.color
					hr.marked = hl.marked
					won = self.solve(hl.id)
				if rr:
					#print("Processing rr event")
					self.mark_action(hr)
					hl.color = hr.color
					hl.marked = hr.marked
					won = self.solve(hr.id)
			hl.draw()
			hr.draw()
		return won
	
	def suspend_player(self, l_player, r_player):
		self.l_player_suspend = l_player
		self.r_player_suspend = r_player
	
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
	def __init__(self, duration, step, name, id, update_action, expiry_action, start_time):
		self.duration = duration
		self.step = step
		self.name = name
		self.id = id
		self.update_action = update_action
		self.expiry_action = expiry_action
		self.start_time = start_time
		
	def format_time(self, time_s):
		return "{:03d}:{:02d}".format(time_s//60, time_s%60)
	
	def __str__(self):
		return "{0} ({1}) = {2}".format(self.name, self.id, self.format_time(self.duration))

	def update(self, current_time):
		if self.duration <= 0:
			self.expiry_action(self)
			return False
		elif (abs(current_time - self.start_time) >= self.step):
			start_time = current_time
			self.update_action(self)
			self.duration -= self.step
			return True
		return True
	
class Question:
	def __init__(self, question = None, answers = None, answer = None):
		self.question = question
		self.answers = answers
		self.answer = answer

class display:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Pravega Hex")
		icon = pygame.image.load("dna-icon.png")
		pygame.display.set_icon(icon)
		self.clock = pygame.time.Clock()
		self.number_of_hexagons = NUMBER_OF_HEXAGONS
		# os.environ["SDL_VIDEO_CENTERED"] = "1"
		self.width = LONG*SCREEN_WIDTH_SCALE
		self.height = LONG*self.number_of_hexagons*SCREEN_HEIGHT_SCALE
		self.display = pygame.display.set_mode((self.width, self.height))
		self.won = True
		self.color = None
		self.xoffset = 560
		self.table = Table(self.display, self.number_of_hexagons, self.xoffset, self.mark_action)
		self.timer_text_loc = (200, 2*self.table.rect_height+((self.height-2*self.table.rect_height)//2))
		self.font = Font()
		self.text_width = 0
		self.timers = []
		self.question_time = 120
		self.time_delta = 1
		self.time_wait = 50
		self.displayed_question = None
		self.display.fill(WHITE)
		self.main()		   

	def add_timer(self, timer):
		self.timers.append(timer)
		self.set_timer()

	def remove_timer(self, timer = None, timer_name = None, timer_id = None):
		if timer:
			self.timers.remove(timer)
		else:
			timers_bk = self.timers.copy()
			for timer in timers_bk:
				if timer.name == timer_name or timer.id == timer_id:
					timers_bk.remove(timer)
			self.timers = timers_bk
	
	def set_timer(self):
		pygame.time.set_timer(TICK_EVENT, self.min_sleep()*1000)
		
	def min_sleep(self):
		return min([self.timers[i].step for i in range(len(self.timers))])
		
	def mark_action(self, hexagon):
		if False: # disabled
			# Do something with a player mark action - show a question
			if hexagon.id > self.table.id_limit:
				if not self.handle_r_question():
					hexagon.unmark()
			else:
				if not self.handle_l_question():
					hexagon.unmark()

	def show_question(self):
		(question, answers, answer) = self.get_question()
		self.display_question(question, answers)
		return answer == self.receive_answer()

	def display_question(self, question, answers):
		# TODO: display question and answers
		self.displayed_question =  Question()# store a reference to the display so that it can be removed

	def get_question(self):
		return (None, None, None)
	
	def receive_answer(self):
		event = pygame.event.wait()
		# synchronously block until some event related to the question occurs
		return None

	def remove_displayed_question(self):
		if self.displayed_question:
			self.displayed_question = None
			# TODO: remove displayed question
			pass

	def handle_r_question(self):
		self.add_timer(Timer(self.question_time, self.time_delta, "R QUESTION ", -1, self.handle_timer_event, self.default_add_r_suspend_timer, time.clock()))
		correct_answer = self.show_question() #This should take time
		if self.displayed_question is None:
			return False
		if not correct_answer:
			self.add_r_suspend_timer(10, self.time_delta)
		self.remove_displayed_question()
		self.remove_timer(timer_name = "R QUESTION ")
		#pygame.time.wait(self.time_wait)
		return correct_answer
	
	def handle_l_question(self):
		self.add_timer(Timer(self.question_time, self.time_delta, "L QUESTION ", -2, self.handle_timer_event, self.default_add_l_suspend_timer, time.clock()))
		correct_answer = self.show_question() #This should take time
		if self.displayed_question is None:
			return False
		if not correct_answer:
			self.add_r_suspend_timer(10, self.time_delta)
		self.remove_displayed_question()
		self.remove_timer(timer_name = "L QUESTION ")
		#pygame.time.wait(self.time_wait)
		return correct_answer
		
	def default_add_r_suspend_timer(self):
		self.remove_displayed_question()
		self.add_r_suspend_timer(10, self.time_delta)
		
	def default_add_l_suspend_timer(self):
		self.remove_displayed_question()
		self.add_l_suspend_timer(10, self.time_delta)

	def min(sequence):
		low = sequence[0]
		for i in sequence:
			if i < low:
				low = i
		return low

	def draw_text(self, raw_text, text_loc, offset):
		tmp_size = self.font.font.size(raw_text)
		if tmp_size[0] > self.text_width:
			self.text_width = tmp_size[0]
		size = (self.text_width, tmp_size[1])
		loc = (text_loc[0], text_loc[1]+offset*(self.font.font.get_linesize()))
		timer_text = self.font.render(raw_text)
		self.display.fill(WHITE, (loc[0], loc[1], size[0], size[1]))
		self.display.blit(timer_text, loc)
		pygame.display.update()
		
	def handle_timer_event(self, timer):
		self.draw_text(str(timer), self.timer_text_loc, timer.id - 1)
	
	def handle_timer_expiry_L_player_resume(self, timer):
		self.handle_timer_expiry(lambda: self.table.suspend_player(False, self.table.r_player_suspend), timer)
		
	def handle_timer_expiry_R_player_resume(self, timer):
		self.handle_timer_expiry(lambda: self.table.suspend_player(self.table.l_player_suspend, False), timer)
	
	def handle_timer_expiry(self, action, timer):
		action()
		self.draw_text("Timer {0} ({1}) Expired".format(timer.name, timer.id), self.timer_text_loc, timer.id - 1)
	
	def main(self):
		global RUN
		self.timer_count = 0
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
			self.clock.tick(10)
		pygame.display.quit()
		pygame.quit()
		quit()
	
	def add_l_suspend_timer(self, duration, step, wait = 0):
		toadd = True
		for timer in self.timers:
			if timer.name == "L SUSPENSION: ":
				toadd = False
		if toadd:
			self.timer_count += 1
			self.table.suspend_player(True, self.table.r_player_suspend)
			self.add_timer(Timer(duration, step, "L SUSPENSION: ", self.timer_count, self.handle_timer_event, self.handle_timer_expiry_L_player_resume, time.clock()))
			#pygame.time.wait(wait)
	
	def add_r_suspend_timer(self, duration, step, wait = 0):
		toadd = True
		for timer in self.timers:
			if timer.name == "R SUSPENSION: ":
				toadd = False
		if toadd:
			self.timer_count += 1
			self.table.suspend_player(self.table.l_player_suspend, True)
			self.add_timer(Timer(duration, step, "R SUSPENSION: ", self.timer_count, self.handle_timer_event, self.handle_timer_expiry_R_player_resume, time.clock()))
			#pygame.time.wait(wait)
		
	def winner(self):
		if self.color == BLUE:
			color = "blue"
		else:
			color = "yellow"

		if self.color:
			r1 = self.font.render(color + " player won!")
		r2 = self.font.render("[Enter/Return] Start")
		r3 = self.font.render("[Esc] Exit")
		
		if self.color:
			self.display.blit(r1, (200,50))
		self.display.blit(r2, (200,200))
		self.display.blit(r3, (200,250))

	def update(self):
		for event in pygame.event.get():
			if event.type == TICK_EVENT:
				timers_bk = self.timers.copy()
				for timer in timers_bk:
					if not timer.update(time.clock()):
						timers_bk.remove(timer)
						self.timer_count -= 1
				self.timers = timers_bk
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				elif event.key == pygame.K_RETURN:
					self.won = False
					self.table.start()
				if event.key == pygame.K_a:
					self.add_l_suspend_timer(10, self.time_delta)
				if event.key == pygame.K_d:
					self.add_r_suspend_timer(10, self.time_delta)
			if event.type == pygame.QUIT:
				return False
		return True

display()