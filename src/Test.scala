import javafx.application.Application
import javafx.scene.Scene
import javafx.scene.image.Image
import javafx.scene.input.{KeyCode, KeyEvent}
import javafx.scene.layout.{Background, BackgroundFill, ColumnConstraints, GridPane}
import javafx.scene.paint.Color
import javafx.stage.Stage

class Test extends Application {
  override def start(primaryStage: Stage) {
    primaryStage.setTitle("Test Question")
    val root = new GridPane
    root.setHgap(100.0)
    val rootConstraintsLeft = new ColumnConstraints
    rootConstraintsLeft.setPercentWidth(50.0)
    val rootConstraintsRight = new ColumnConstraints
    rootConstraintsRight.setPercentWidth(50.0)
    root.getColumnConstraints.addAll(rootConstraintsLeft, rootConstraintsRight)
    val parameters = getParameters.getRaw
    val qdisp = new QuestionDisplay(Quiz.loadQuiz(parameters.get(0)),
      (parameters.get(1).toDouble, parameters.get(2).toDouble, parameters.get(3).toDouble))
    root.add(new HexDisplay(qdisp, 800, 720), 0, 0)
    qdisp.setVisible(true)
    root.add(qdisp, 1, 0)
    root.setBackground(new Background(new BackgroundFill(Color.SILVER, null, null)))
    root.autosize()
    val scene = new Scene(root, 1370, 720)
    primaryStage.getIcons.add(new Image(classOf[Test].getResourceAsStream("/images/icon.png")))
    scene.setOnKeyPressed((ke: KeyEvent) => {
      if (ke.getCode == KeyCode.ESCAPE) {
        primaryStage.close()
      }
    })
    primaryStage.setScene(scene)
    primaryStage.show()
  }
}

object Test {
  def main(args: Array[String]): Unit = {
    Application.launch(classOf[Test], args: _*)
  }
}