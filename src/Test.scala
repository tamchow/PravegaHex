import javafx.application.Application
import javafx.event.EventHandler
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
    root.setHgap(0.0)
    val rootConstraints = new ColumnConstraints
    rootConstraints.setPercentWidth(50.0)
    root.getColumnConstraints.addAll(rootConstraints, rootConstraints)
    val qdisp = new QuestionDisplay(Quiz.loadQuiz(getParameters.getRaw.get(0)), (0, 15, -15))
    root.add(new HexDisplay(qdisp, 800, 720), 0, 0)
    qdisp.setVisible(true)
    root.add(qdisp, 1, 0)
    root.setBackground(new Background(new BackgroundFill(Color.SILVER, null, null)))
    root.autosize()
    val scene = new Scene(root, 1370, 720)
    primaryStage.getIcons.add(new Image(classOf[Test].getResourceAsStream("/images/icon.png")))
    scene.setOnKeyPressed(new EventHandler[KeyEvent]() {
      def handle(ke: KeyEvent) {
        if (ke.getCode == KeyCode.ESCAPE) {
          primaryStage.close()
        }
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