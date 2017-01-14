import java.io.{File, FileNotFoundException}

/**
  * Encapsulates a Quiz
  */
case class Quiz(questions: Seq[Question])

object Quiz{
  def loadQuiz(folderPath: String) = Quiz(new File(folderPath).listFiles.map(x => Question.loadQuestion(x.getAbsolutePath)))
}
/**
  * Encapsulates a question
  */
case class Question(content: String, answers: Seq[Answer])

object Question{
  def loadQuestion(folderPath: String): Question = {
    val files = new File(folderPath).listFiles
    val question = files.find(_.getName.toLowerCase.contains("question")).
      getOrElse(throw new FileNotFoundException("No Question File"))
    val answers = files.filter(_.getName.toLowerCase.contains("answer")).
      map(_.getAbsolutePath).map(Answer.loadAnswer)
    Question(io.Source.fromFile(question).mkString, answers)
  }
}
/**
  * Encapsulates an answer
  */
case class Answer(content: String, isCorrectAnswer: Boolean)

object Answer{
  def loadAnswer(filePath: String): Answer = Answer(io.Source.fromFile(filePath).mkString,
    filePath.toLowerCase.contains("correct answer"))
}