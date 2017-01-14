import os
import random
import time
from threading import Thread
import pygame

# constants
RUN = True
LENGTH = 40
RECTANGLE_WIDTH_SCALE = 1.421
SCREEN_WIDTH_SCALE = 16
RECTANGLE_HEIGHT_SCALE = 1
SCREEN_HEIGHT_SCALE = 3
YELLOW = (255, 231, 0)
BLUE = (0, 127, 245)
WHITE = (255,255,255)
BLACK = (0,0,0)
BORDER_COLOR = (100,100,100)
LEFT = 1
RIGHT = 3
NUMBER_OF_HEXAGONS = 6
INITIAL_BLUE_SCORE = 0
INITIAL_YELLOW_SCORE = 0
player = random.choice((BLUE, YELLOW))

def check_player():
	global player
	
	if player == BLUE:
		player = YELLOW
	elif player == YELLOW:
		player = BLUE
		

class Font:

	def __init__(self):
		pygame.font.init()
		self.font = pygame.font.Font("cubicfive10.ttf", 20)

	def render(self, text):
		return self.font.render(text, False, BLACK)

import sys
import os
import random
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QApplication)
from PyQt5.QtCore import (QCoreApplication, QUrl, QByteArray)
from PyQt5.QtWebEngineWidgets import QWebEngineView

CORRECT_ANSWER_POINTS = +15
INCORRECT_ANSWER_POINTS = -15
PASS_POINTS = 0
#INVALID_POINTS = -sys.maxsize - 1

class QuestionDisplay(QWidget):
	
	def __init__(self, question, questions, id):
		super().__init__()
		self.reinit(question, questions, id)
		
	def find_answer_by_label(self, label):
		for answer in self.question.answers:
			if answer.content == label:
				return answer
		return None
	
	def show(self):
		self.show()
	
	def clear(layout):
		for i in reversed(range(layout.count())): 
			widgetToRemove = layout.itemAt( i ).widget()
			# remove it from the layout list
			layout.removeWidget( widgetToRemove )
			# remove it from the gui
			widgetToRemove.setParent(None)
	
	def reinit(self, question, questions, id):
		clear(self.grid)
		self.score = None
		self.question = question
		self.questions = questions
		self.id = id
		self.initUI()
		
	def input_handler(self, score = None):
		sender = self.sender()
		answer_points = PASS_POINTS
		if not (sender.text() == "Pass"):
			answer = self.find_answer_by_label(sender.text())
			answer_points = CORRECT_ANSWER_POINTS if answer.is_correct_answer else INCORRECT_ANSWER_POINTS
		if score is None:
			self.score = answer_points
		else:
			self.score = score
		self.questions.remove_question(self.question)
		self.close()
		
	def launch(argv, question, questions, id = 0):
		app = QApplication(argv)
		display = QuestionDisplay(question, questions, id)
		app.exec_()
		return display
		
	def initUI(self):
		
		webview = QWebEngineView(self)
		webview.setHtml(self.question.content)
		webview.show()

		self.grid = QGridLayout()
		grid.setSpacing(10)
		
		passbtn = QPushButton("Pass", self)
		passbtn.clicked.connect(lambda: self.input_handler(None))
		passbtn.resize(passbtn.sizeHint())

		answer_buttons = []
		for answer in self.question.answers:
			answer_button = QPushButton(answer.content, self)
			answer_button.clicked.connect(lambda: self.input_handler(None))
			answer_button.resize(answer_button.sizeHint())
			answer_buttons.append(answer_button)
			
		self.grid.addWidget(webview, 1, 1)
		self.grid.addWidget(passbtn, 1, 2)
		
		for idx, answer_button in enumerate(answer_buttons):
			self.grid.addWidget(answer_button, idx+3, 1)
		
		self.setLayout(self.grid) 
		
		self.setGeometry(300, 300, 1280, 720)
		self.setWindowTitle("Question {0}".format(self.id))

class Questions(object):
	def __init__(self, questions):
		self.questions = questions
	
	def get_question(self):
		random.shuffle(self.questions)
		return self.questions[0]
	
	def remove_question(self, question):
		self.questions.remove(question)
		
	def load_questions(quiz_folder):
		questions = []
		for folder_path in os.listdir(quiz_folder):
			questions.append(Question.load_question(os.path.join(quiz_folder, folder_path)))
		return Questions(questions)
		
class Question(object):
	def __init__(self, content, answers):
		self.content = content
		self.answers = answers
		
	def load_question(question_folder):
		content = None
		answers = []
		for file_path in os.listdir(question_folder):
			canonical_path = os.path.join(question_folder, file_path)
			if "Question" in file_path:
				with open(canonical_path, "r") as qfile:
					content = qfile.read()
			elif "Answer" in file_path:
				answers.append(Answer.load_answer(canonical_path))
		return Question(content, answers)
		
class Answer(object):
	def __init__(self, content, is_correct_answer = False):
		self.content = content
		self.is_correct_answer = is_correct_answer
		
	def load_answer(answer_file):
		with open(answer_file, "r") as content:
				return Answer(content.read(), "correct answer" in answer_file.lower()) if "Answer" in answer_file else None

class Hexagon:
	def __init__(self, display, x, y, id, blue_start, blue_end, yellow_start, yellow_end):
		self.display = display
		self.d = LENGTH
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
		a = chr((self.id % NUMBER_OF_HEXAGONS) + 65)
		d = (self.id // NUMBER_OF_HEXAGONS) + 1
		self.rendered_id = Font().render(str(a)+str(d))
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
		self.display.blit(self.rendered_id,(self.x-self.d/4,self.y-self.d/4))

	def update(self, x, y, player):
		c = self.rect.collidepoint(x, y)
		if c and player and (not self.marked) and self.color == WHITE:
				check_player()
				#self.mark()
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
		self.rect_width = LENGTH*number_of_hexagons*RECTANGLE_WIDTH_SCALE
		self.rect_height = (LENGTH*number_of_hexagons+1)*RECTANGLE_HEIGHT_SCALE
		self.xoffset = 2*self.rect_width + xoffset
		self.id_limit = 0
		self.mark_action = mark_action
		self.start()
		
	def start(self):
		self.hexagons = {}
		self.id = 0
		dx = LENGTH
		dy = LENGTH*self.number_of_hexagons
		# Table
		for i in range(self.number_of_hexagons):
			for e in range(self.number_of_hexagons):
				x = dx + LENGTH*(e + i)*1.5
				y = dy + LENGTH*(i - e)
				blue_start, blue_end, yellow_start, yellow_end = self.edge(self.id)
				self.hexagons[self.id] = Hexagon(self.display, x, y, self.id, blue_start, blue_end, yellow_start, yellow_end)
				self.id += 1
		self.id_limit = self.id
				
	def edge(self, id):
		id += 1
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
		x, y = pygame.mouse.get_pos()		 
		clicked = pygame.event.wait().type == pygame.MOUSEBUTTONDOWN
		won = None
		for (id, h) in self.hexagons.items():
			if h.update(x, y, clicked):
				if self.mark_action(h):
					h.mark()
					won = self.solve(h.id)
			h.draw()
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

class Display:
	def __init__(self):
		self.blue_score = INITIAL_BLUE_SCORE
		self.yellow_score = INITIAL_YELLOW_SCORE
		pygame.init()
		pygame.display.set_caption("Pravega Bio Quiz - Hex")
		icon = pygame.image.load("dna-icon.png")
		pygame.display.set_icon(icon)
		self.clock = pygame.time.Clock()
		self.number_of_hexagons = NUMBER_OF_HEXAGONS
		# os.environ["SDL_VIDEO_CENTERED"] = "1"
		self.width = LENGTH*SCREEN_WIDTH_SCALE
		self.height = LENGTH*self.number_of_hexagons*SCREEN_HEIGHT_SCALE
		self.display = pygame.display.set_mode((self.width, self.height))
		self.won = True
		self.questions = Questions.load_questions("./Trial/Questions/")
		self.color = None
		self.xoffset = 0
		self.table = Table(self.display, self.number_of_hexagons, self.xoffset, self.mark_action)
		#self.timer_text_loc = (200, 2*self.table.rect_height+((self.height-2*self.table.rect_height)//2))
		self.font = Font()
		self.text_width = 0
		self.display.fill(WHITE)
		self.main()
		
	def mark_action(self, hexagon):
		"""question_display = QuestionDisplay.launch(sys.argv, self.questions.get_question(), self.questions, hexagon.id)
		while question_display.score is None:
			pygame.time.delay(1)
		score = question_display.score
		self.questions = question_display.questions
		print(score)
		if player == BLUE:
			self.blue_score += score
		elif player == YELLOW:
			self.yellow_score += score
		#question_display.kill()
		return score > 0"""
		print(hexagon.id)
		return True
		
		

	def draw_text(self, raw_text, text_loc, offset):
		tmp_size = self.font.font.size(raw_text)
		if tmp_size[0] > self.text_width:
			self.text_width = tmp_size[0]
		size = (self.text_width, tmp_size[1])
		loc = (text_loc[0], text_loc[1]+offset*(self.font.font.get_linesize()))
		text = self.font.render(raw_text)
		self.display.fill(WHITE, (loc[0], loc[1], size[0], size[1]))
		self.display.blit(text, loc)
		pygame.display.update()
		
	def main(self):
		while self.update():
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
			self.clock.tick(1)
		pygame.display.quit()
		pygame.quit()
		quit()
		
	def winner(self):
		if self.color == BLUE:
			color = "blue"
		else:
			color = "yellow"

		if self.color:
			r1 = self.font.render("{0} player won with {1} points!".format(color, self.blue_score if self.color == BLUE else self.yellow_score))
		r2 = self.font.render("[Enter/Return] Start")
		r3 = self.font.render("[Esc] Exit")
		
		if self.color:
			self.display.blit(r1, (200,50))
		self.display.blit(r2, (200,200))
		self.display.blit(r3, (200,250))

	def update(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				elif event.key == pygame.K_RETURN:
					self.won = False
					self.table.start()
			if event.type == pygame.QUIT:
				return False
		return True

Display()