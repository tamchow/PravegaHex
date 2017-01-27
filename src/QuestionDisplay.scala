import javafx.event.{ActionEvent, EventHandler}
import javafx.geometry.{HPos, Pos}
import javafx.scene.control.Button
import javafx.scene.layout._
import javafx.scene.paint.Color
import javafx.scene.text.TextAlignment
import javafx.scene.web.WebView

/**
  * JavaFX question display UI
  */
class QuestionDisplay(var quiz: Quiz, points: (Double, Double, Double)) extends GridPane {
  var score: java.lang.Double = _
  var question: Question = _
  val (pass_POINTS, correct_POINTS, incorrect_POINTS) = points

  def prepareNewQuestion(onInput: Double => Unit) {
    getChildren.clear()
    getColumnConstraints.clear()
    setVisible(false)
    setAlignment(Pos.CENTER)
    setVgap(10)
    setHgap(10)
    setMaxSize(java.lang.Double.MAX_VALUE, java.lang.Double.MAX_VALUE)
    question = util.Random.shuffle(quiz.questions).head
    score = null
    val passPane = new BorderPane
    val passButton = new Button("Pass")
    passButton.setTextAlignment(TextAlignment.CENTER)
    passButton.addEventHandler(ActionEvent.ACTION, new QuestionEventHandler(question.answers, onInput))
    passButton.setMaxWidth(java.lang.Double.MAX_VALUE)
    passButton.setPrefHeight(40)
    passButton.autosize()
    passPane.setCenter(passButton)
    val questionDisplay = new WebView
    questionDisplay.getEngine.loadContent(question.content)
    questionDisplay.autosize()
    val answerDisplay = new GridPane
    //answerDisplay.setBackground(new Background(new BackgroundFill(Color.YELLOW, null, null)))
    answerDisplay.setAlignment(Pos.CENTER)
    answerDisplay.setVgap(10)
    val answerButtons = question.answers.map(x => createAnswerButton(x, new QuestionEventHandler(question.answers, onInput)))
    val leftHConstraint = new ColumnConstraints
    leftHConstraint.setHalignment(HPos.CENTER)
    leftHConstraint.setPercentWidth(80.0)
    val rightHConstraint = new ColumnConstraints
    rightHConstraint.setHalignment(HPos.CENTER)
    rightHConstraint.setPercentWidth(20.0)
    getColumnConstraints.addAll(leftHConstraint, rightHConstraint)
    val answerDisplayConstraints = new ColumnConstraints
    answerDisplayConstraints.setPercentWidth(100)
    answerDisplayConstraints.setHalignment(HPos.CENTER)
    answerDisplay.getColumnConstraints.add(answerDisplayConstraints)
    add(questionDisplay, 0, 0)
    add(answerDisplay, 0, 1)
    add(passPane, 1, 0)
    autosize()
    for((button, index) <- answerButtons.zipWithIndex){
      answerDisplay.add(button, 0, index)
    }
    //setBackground(new Background(new BackgroundFill(Color.BLUE, null, null)))
    setVisible(true)
  }

  private def createAnswerButton(answer: Answer, eventHandler: QuestionEventHandler): Button = {
    val answerButton = new Button(answer.content)
    answerButton.setTextAlignment(TextAlignment.CENTER)
    answerButton.setBackground(new Background(
      new BackgroundFill(if(answer.isCorrectAnswer) Color.GREEN else Color.RED, null, null)))
    answerButton.setTextFill(Color.WHITE)
    answerButton.addEventHandler(ActionEvent.ACTION, eventHandler)
    answerButton.setMaxWidth(java.lang.Double.MAX_VALUE)
    answerButton.autosize()
    answerButton
  }

  private class QuestionEventHandler(answers: Seq[Answer], callback: Double => Unit) extends EventHandler[ActionEvent] {
    def handle(e: ActionEvent) {
      e.getSource match {
        case fromButton: Button =>
          if (fromButton.getText.toLowerCase.contains("pass")) score = pass_POINTS
          else if (answers.exists(x => fromButton.getText.contains(x.content) && x.isCorrectAnswer)) score = correct_POINTS
          else score = incorrect_POINTS
      }
      setVisible(false)
      callback(score)
    }
  }

}
