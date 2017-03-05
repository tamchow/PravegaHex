import javafx.application.Platform
import javafx.concurrent.Task
import javafx.event.EventHandler
import javafx.geometry.Rectangle2D
import javafx.scene.canvas.{Canvas, GraphicsContext}
import javafx.scene.input.MouseEvent
import javafx.scene.paint.Color
import javafx.scene.text.{Font, FontWeight, TextAlignment}

/**
  * Encapsulates a hexagon cell
  */
case class Hexagon(display: GraphicsContext, x: Double, y: Double, id: Int,
                   blue_start: Boolean, blue_end: Boolean, yellow_start: Boolean, yellow_end: Boolean) {

  import HexConstants._

  private lazy val (xs, ys) = vertices.toArray.unzip
  val d = LENGTH
  val (dx, dy) = (d, Math.sqrt(3.0) * d / 2.0)
  val rendered_id = s"$alpha$digit"
  val vertices = IndexedSeq(
    (x - d, y),
    (x - d / 2, y - d),
    (x + d / 2, y - d),
    (x + d, y),
    (x + d / 2, y + d),
    (x - d / 2, y + d))
  val boundingRect = new Rectangle2D(x - dx, y - dy, 2 * dx, 2 * dy)
  private val alpha: Char = (id % NUMBER_OF_HEXAGONS + 65).asInstanceOf[Char]
  private val digit = (id / NUMBER_OF_HEXAGONS) + 1
  var color = BLANK
  var marked = false

  def draw() {
    display.save()
    display.setFill(color)
    display.setStroke(BORDER_COLOR)
    display.fillPolygon(xs, ys, xs.length)
    display.strokePolygon(xs, ys, xs.length)
    display.restore()
    display.save()
    display.setStroke(if (color.grayscale.getGreen /*Choose any channel*/ > 0.5 /*1.0 is white, 0.0 is black*/ )
      BLACK else BLANK)
    display.strokeText(rendered_id, x - d / 8, y + d / 8)
    display.restore()
  }

  def update(x: Double, y: Double, player: Boolean, playerColor: Color): Boolean =
    contains(x, y) &&
      player && !marked &&
      (color == BLANK || color == FOCUS)

  def contains(x_ : Double, y_ : Double): Boolean = {
    if (boundingRect.contains(x_, y_)) {
      var c: Boolean = false
      var j = 5 //vertexCount - 1
      for (i <- 0 until 6 /*vertexCount*/ ) {
        if (((ys(i) > y_) != (ys(j) > y_)) &&
          (x_ < (xs(j) - xs(i)) * (y_ - ys(i)) / (ys(j) - ys(i)) + xs(i))) {
          c = !c
        }
        j = i
      }
      c
    }
    else false
  }

  def mark(playerColor: Color): Unit = {
    color = playerColor
    marked = true
  }

  def focus(): Unit = {
    color = FOCUS
  }

  def unmark(): Unit = {
    defocus()
    marked = false
  }

  def defocus(): Unit = {
    color = BLANK
  }
}

case class Table(display: Canvas, number_of_hexagons: Int, xoff: Int, markAction: () => Unit, onWin: Color => Unit) {

  import HexConstants._

  lazy val bugCheck: String = hexagons.map(_.id).
    map(id => s"$id is member of edges ${nameEdges(edge(id))}and has neighbours: ${Neighbours(edge(id)).map(_ + id)}").
    mkString("\n")
  val rect_width: Double = LENGTH * number_of_hexagons * RECTANGLE_WIDTH_SCALE
  val rect_height: Int = (LENGTH * number_of_hexagons + 1) * RECTANGLE_HEIGHT_SCALE
  val xoffset: Double = 2 * rect_width + xoff
  val Neighbours = Map((true, false, true, false) -> Seq(1, number_of_hexagons, number_of_hexagons + 1),
    (false, true, true, false) -> Seq(-1, number_of_hexagons, number_of_hexagons - 1),
    (true, false, false, true) -> Seq(1, -number_of_hexagons, -number_of_hexagons + 1),
    (false, true, false, true) -> Seq(-1, -number_of_hexagons, -number_of_hexagons - 1),
    (true, false, false, false) -> Seq(1, number_of_hexagons, number_of_hexagons + 1,
      -number_of_hexagons, -number_of_hexagons + 1),
    (false, true, false, false) -> Seq(-1, number_of_hexagons, number_of_hexagons - 1,
      -number_of_hexagons, -number_of_hexagons - 1),
    (false, false, true, false) -> Seq(1, -1, number_of_hexagons, number_of_hexagons - 1, number_of_hexagons + 1),
    (false, false, false, true) -> Seq(1, -1, -number_of_hexagons, -number_of_hexagons - 1, -number_of_hexagons + 1),
    (false, false, false, false) -> Seq(-1, +1, number_of_hexagons, -number_of_hexagons,
      number_of_hexagons + 1, number_of_hexagons - 1, -number_of_hexagons + 1, -number_of_hexagons - 1))
  private val gc = display.getGraphicsContext2D
  var playerColor: Color = PLAYER_2_COLOR
  display.addEventHandler(MouseEvent.MOUSE_PRESSED, new MouseEventHandler())
  start()
  //if (util.Random.nextBoolean()) BLUE else YELLOW
  var hexagons: Seq[Hexagon] = Seq()
  var ignoreInput = false
  var toMark: (Double, Double, Boolean) = _

  def start() {
    var id = 0
    val dx = LENGTH
    val dy = LENGTH * number_of_hexagons
    //Table
    for (i <- 0 until number_of_hexagons) {
      for (e <- 0 until number_of_hexagons) {
        val x = dx + LENGTH * (e + i) * 1.5
        val y = dy + LENGTH * (i - e)
        val (blue_start, blue_end, yellow_start, yellow_end) = edge(id)
        hexagons :+= Hexagon(gc, x, y, id, blue_start, blue_end, yellow_start, yellow_end)
        id += 1
      }
    }
    gc.save()
    gc.setFill(PLAYER_2_COLOR)
    gc.fillRect(0, 0, rect_width, rect_height)
    gc.fillRect(rect_width, rect_height, rect_width, rect_height)
    gc.setFill(PLAYER_1_COLOR)
    gc.fillRect(rect_width, 0, rect_width, rect_height)
    gc.fillRect(0, rect_height, rect_width, rect_height)
    gc.restore()
  }

  def edge(id: Int): (Boolean, Boolean, Boolean, Boolean) = {
    //corner <
    if (id == 0) (true, false, true, false)
    //corner ^
    else if (id == number_of_hexagons - 1) (false, true, true, false)
    //corner v
    else if (id == number_of_hexagons * (number_of_hexagons - 1)) (true, false, false, true)
    //corner >
    else if (id == (number_of_hexagons * number_of_hexagons) - 1) (false, true, false, true)
    //edge <v blue_start
    else if (id % number_of_hexagons == 0) (true, false, false, false)
    //edge <^ yellow_start
    else if (id >= 0 && id < number_of_hexagons) (false, false, true, false)
    //edge ^> blue_end
    else if ((id + 1) % number_of_hexagons == 0) (false, true, false, false)
    //edge v> yellow_end
    else if (id >= number_of_hexagons * (number_of_hexagons - 1) &&
      (id < number_of_hexagons * number_of_hexagons)) (false, false, false, true)
    //internal
    else (false, false, false, false)
  }

  def draw() {
    for (hexagon <- hexagons) {
      hexagon.draw()
    }
  }

  def markPending(willMark: Boolean): Unit = {
    val (x, y, clicked) = toMark
    val h = findHexagonContaining(x, y)
    if (h.marked) h.unmark() else h.defocus()
    if (willMark) {
      var won: Option[Color] = None
      if (h.update(x, y, clicked, playerColor)) {
        h.mark(playerColor)
        won = solve(h.id)
      }
      won match {
        case Some(color) => onWin(color)
        case None => ()
      }
    }
    h.draw()
    playerColor = complementaryColor(playerColor)
  }

  def findHexagonContaining(x: Double, y: Double): Hexagon = hexagons.find(_.contains(x, y)).
    getOrElse(throw new NoSuchElementException(s"Click point ($x,$y) doesn't exist"))

  def nameEdges(edges: (Boolean, Boolean, Boolean, Boolean)): String = {
    var str = ""
    if (edges._1) str += "blue_start, "
    if (edges._2) str += "blue_end, "
    if (edges._3) str += "yellow_start, "
    if (edges._4) str += "yellow_end, "
    if (str.isEmpty) "none " else str
  }

  private def solve(id: Int) = {
    val color = hexagons(id).color
    val chain = around(id, color, Seq())
    if (beginning(chain, color) && end(chain, color)) Some(color) else None
  }

  private def around(id: Int, color: Color, seen: Seq[Int]): Seq[Int] = {
    //val chain = [hexagons(h).id for h in around_ if (hexagons(h).color == color)]
    val chain = Neighbours(edge(id)).map(_ + id).filter(h => hexagons(h).color == color && !seen.contains(h))
    var seen_ = seen ++ chain
    for (i <- chain) {
      seen_ ++= around(i, color, seen_)
    }
    seen_
  }

  private def beginning(chain: Seq[Int], color: Color) = color match {
    case PLAYER_1_COLOR => chain.exists(c => hexagons(c).blue_start)
    case PLAYER_2_COLOR => chain.exists(c => hexagons(c).yellow_start)
  }

  private def end(chain: Seq[Int], color: Color) = color match {
    case PLAYER_1_COLOR => chain.exists(c => hexagons(c).blue_end)
    case PLAYER_2_COLOR => chain.exists(c => hexagons(c).yellow_end)
  }

  class MouseEventHandler() extends EventHandler[MouseEvent] {
    override def handle(event: MouseEvent): Unit = {
      if (!ignoreInput) {
        val (x, y) = (event.getSceneX, event.getSceneY)
        val clicked = event.isPrimaryButtonDown || event.isSecondaryButtonDown
        val selectedHexagon = findHexagonContaining(x, y)
        selectedHexagon.focus()
        selectedHexagon.draw()
        toMark = (x, y, clicked)
        markAction()
      }
    }
  }
}

class HexDisplay(questionDisplay: QuestionDisplay, width: Int, height: Int) extends Canvas(width, height) {

  val table = Table(this, NUMBER_OF_HEXAGONS, 0, markAction _, onWin)

  import HexConstants._
  var (yellowScore, blueScore) = (0.0, 0.0)

  def markAction(): Unit = {
    table.ignoreInput = true
    try {
      questionDisplay.prepareNewQuestion(update)
    } catch {
      case _: Exception =>
        val errorText = "Ran out of questions, exiting in 5 seconds"
        clearScreen()
        questionDisplay.setVisible(false)
        renderText(errorText, color = BLACK, fontHeightMultiplier = 1.75)
        new Thread(new CloseDownTask).start()
    }
  }

  table.draw()
  renderText(s"Blue : $blueScore points", y = 4 * getHeight / 5, color = PLAYER_1_COLOR,
    yOffset = -(getGraphicsContext2D.getFont.getSize + 5), fontHeightMultiplier = 1.25)
  renderText(s"Yellow : $yellowScore points", y = 4 * getHeight / 5, color = PLAYER_2_COLOR,
    yOffset = getGraphicsContext2D.getFont.getSize + 5, fontHeightMultiplier = 1.25)
  setVisible(true)

  def update(score: Double): Unit = {
    val (currentYellowScore, currentBlueScore) = (yellowScore, blueScore)
    table.playerColor match {
      case PLAYER_2_COLOR => yellowScore += score
      case PLAYER_1_COLOR => blueScore += score
    }
    getGraphicsContext2D.clearRect(0, 7 * getHeight / 10, getWidth, 3 * getHeight / 10)
    renderText(s"Blue : $blueScore points", y = 4 * getHeight / 5, color = PLAYER_1_COLOR,
      yOffset = -(getGraphicsContext2D.getFont.getSize + 5), fontHeightMultiplier = 1.25)
    renderText(s"Yellow : $yellowScore points", y = 4 * getHeight / 5, color = PLAYER_2_COLOR,
      yOffset = getGraphicsContext2D.getFont.getSize + 5, fontHeightMultiplier = 1.25)
    val answeredCorrectly = blueScore > currentBlueScore || yellowScore > currentYellowScore
    if (answeredCorrectly) {
      import questionDisplay._
      quiz = Quiz(quiz.questions.filter(_ != question))
    }
    table.markPending(answeredCorrectly)
    table.ignoreInput = false
  }

  def onWin(color: Color): Unit = {
    clearScreen()
    val winnerNLoser = color match {
      case PLAYER_2_COLOR => (("Yellow", yellowScore), ("Blue", blueScore))
      case PLAYER_1_COLOR => (("Blue", blueScore), ("Yellow", yellowScore))
    }
    val winText = s"${winnerNLoser._1._1} player won with ${winnerNLoser._1._2} points."
    val loseText = s"Losing player ${winnerNLoser._2._1} scored ${winnerNLoser._2._2} points."
    val textLength = winText.length max loseText.length
    renderText(winText, textLength = textLength,
      yOffset = -(getGraphicsContext2D.getFont.getSize + 5), fontHeightMultiplier = 1.75, color = color)
    renderText(loseText, textLength = textLength,
      yOffset = getGraphicsContext2D.getFont.getSize + 5, fontHeightMultiplier = 1.75, color = complementaryColor(color))
  }

  private def clearScreen() = getGraphicsContext2D.clearRect(0, 0, getWidth, getHeight)

  def renderText(text: String, textLength: Int = -1, x: Double = getWidth / 2, y: Double = getHeight / 2,
                 yOffset: Double = 0, color: Color = null, fontHeightMultiplier: Double = 1.0): Unit = {
    val gc = getGraphicsContext2D
    gc.save()
    gc.setFont(Font.font(gc.getFont.getFamily, FontWeight.BOLD, gc.getFont.getSize * fontHeightMultiplier))
    gc.setFill(color)
    gc.setStroke(color)
    val textDimension = gc.getFont.getSize
    val xOffset = textDimension * (if (textLength < 0) text.length else textLength) / 8
    val (xStart, yStart) = (x - xOffset, y + yOffset)
    gc.setTextAlign(TextAlignment.CENTER)
    gc.fillText(text, xStart, yStart)
    gc.restore()
  }

  class CloseDownTask extends Task[Unit] {
    override def call(): Unit = {
      Thread.sleep(5000)
      Platform.exit()
    }
  }

}

object HexConstants {
  val LENGTH = 40
  val RECTANGLE_WIDTH_SCALE = 1.421
  val SCREEN_WIDTH_SCALE = 20
  val RECTANGLE_HEIGHT_SCALE = 1
  val SCREEN_HEIGHT_SCALE = 3
  val PLAYER_2_COLOR = Color.YELLOW
  val PLAYER_1_COLOR = Color.BLUE
  val BLANK = Color.WHITE
  val FOCUS = Color.CORAL
  val BLACK = Color.BLACK
  val BORDER_COLOR = Color.GRAY
  val NUMBER_OF_HEXAGONS = 6

  def complementaryColor(color: Color): Color = color match {
    case PLAYER_1_COLOR => PLAYER_2_COLOR
    case PLAYER_2_COLOR => PLAYER_1_COLOR
  }
}

