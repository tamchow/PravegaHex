import sys
import os
import random
from threading import Thread
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QApplication)
from PyQt5.QtCore import (QCoreApplication, QTimer)
from PyQt5.QtWebEngineWidgets import QWebEngineView

CORRECT_ANSWER_POINTS = +15
INCORRECT_ANSWER_POINTS = -15
PASS_POINTS = 0
display = None
#INVALID_POINTS = -sys.maxsize - 1

class QuestionDisplay(QWidget):
	
	def __init__(self, question, questions, id):
		super().__init__()
		self.pending_actions = []
		timer = QTimer()
		timer.start(500)  # You may change this if you wish.
		timer.timeout.connect(self.handle_pending_actions)  # Let the interpreter run each 500 ms.
		self.grid = None
		self.reinit(question, questions, id)
	
	def handle_pending_actions(self):
		for action in self.pending_actions:
			action()

	def find_answer_by_label(self, label):
		for answer in self.question.answers:
			if answer.content == label:
				return answer
		return None
	
	def clear(self, layout):
		for i in reversed(range(layout.count())): 
			widgetToRemove = layout.itemAt(i).widget()
			layout.removeWidget(widgetToRemove)
			widgetToRemove.setParent(None)
	
	def kill(self):
		self.hide()
		#self.close()
		#QCoreApplication.exit(0)
				
	
	def reinit(self, question, questions, id = 0):
		#if self.isVisible():
		#	self.close()
		#	print("closed")
		#if self.grid is not None:
		#	self.clear(self.grid)
		self.score = None
		self.question = question
		self.questions = questions
		self.id = id
		self.initUI()
		self.show()
		
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
		self.kill()
		
	def launch(argv, question, questions, id = 0):
		global display
		Thread(target=lambda: QuestionDisplay.show_app(argv, question, questions, id), daemon=True).start()
		print("return")
		#return display
	
	def show_app(argv, question, questions, id = 0):
		global display
		print("core init")
		app = QApplication(argv)
		print("app init")
		display = QuestionDisplay(question, questions, id)
		print("app start")
		app.exec_()

	def initUI(self):
		
		webview = QWebEngineView(self)
		webview.setHtml(self.question.content)
		webview.show()

		self.grid = QGridLayout()
		self.grid.setSpacing(10)
		
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
		
class Answer(object):
	def __init__(self, content, is_correct_answer = False):
		self.content = content
		self.is_correct_answer = is_correct_answer
		
	def load_answer(answer_file):
		with open(answer_file, "r") as content:
				return Answer(content.read(), "correct answer" in answer_file.lower()) if "Answer" in answer_file else None
		
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

def main():
	global display
	questions = Questions.load_questions("./Trial/Questions/")
	print("showing initial")
	QuestionDisplay.launch(sys.argv, questions.get_question(), questions)
	print("shown, now waiting")
	while display.isVisible():
		print("still waiting")
	print("received input, window hidden")
	print("showing window again")
	QuestionDisplay.launch(sys.argv, questions.get_question(), questions)
	print("window shown again")
	
if __name__ == '__main__':
	main()