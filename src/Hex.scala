import javafx.application.Platform
import javafx.concurrent.{Service, Task}
import javafx.event.EventHandler
import javafx.scene.canvas.{Canvas, GraphicsContext}
import javafx.scene.paint.Color
import javafx.geometry.Rectangle2D
import javafx.scene.input.MouseEvent
import javafx.scene.text.{Font, FontWeight, TextAlignment}

import scala.runtime.Nothing$

object HexConstants {
  val LENGTH = 40
  val RECTANGLE_WIDTH_SCALE = 1.421
  val SCREEN_WIDTH_SCALE = 20
  val RECTANGLE_HEIGHT_SCALE = 1
  val SCREEN_HEIGHT_SCALE = 3
  val YELLOW = Color.YELLOW
  val BLUE = Color.BLUE
  val WHITE = Color.WHITE
  val BLACK = Color.BLACK
  val BORDER_COLOR = Color.GRAY
  val NUMBER_OF_HEXAGONS = 6

  def complementaryColor(color: Color): Color = color match {
    case BLUE => YELLOW
    case YELLOW => BLUE
  }
}

/**
  * Encapsulates a hexagon cell
  */
case class Hexagon(display: GraphicsContext, x: Double, y: Double, id: Int,
                   blue_start: Boolean, blue_end: Boolean, yellow_start: Boolean, yellow_end: Boolean) {

  import HexConstants._

  val d = LENGTH
  var color = WHITE
  var marked = false
  private val alpha: Char = (id % NUMBER_OF_HEXAGONS + 65).asInstanceOf[Char]
  private val digit = (id / NUMBER_OF_HEXAGONS) + 1
  val rendered_id = s"$alpha$digit"
  val rect = new Rectangle2D(x - d / 2 - 4, y - d, d + 8, d * 2)

  def draw() {
    val (xs, ys) = Array((x - d, y), (x - d / 2, y - d), (x + d / 2, y - d), (x + d, y), (x + d / 2, y + d), (x - d / 2, y + d)).unzip
    display.save()
    display.setFill(color)
    display.setStroke(BORDER_COLOR)
    display.fillPolygon(xs, ys, xs.length)
    display.strokePolygon(xs, ys, xs.length)
    display.restore()
    display.save()
    display.setStroke(BLACK)
    display.strokeText(rendered_id, x - d / 8, y + d / 8)
    display.restore()
  }

  def update(x: Double, y: Double, player: Boolean, playerColor: Color): Boolean = rect.contains(x, y) && player && !marked && color == WHITE


  def mark(playerColor: Color) {
    color = playerColor
    marked = true
  }

  def unmark() {
    color = WHITE
    marked = false
  }
}

case class Table(display: Canvas, number_of_hexagons: Int, xoff: Int, markAction: () => Unit, onWin: Color => Unit) {

  import HexConstants._

  private val gc = display.getGraphicsContext2D

  val rect_width: Double = LENGTH * number_of_hexagons * RECTANGLE_WIDTH_SCALE
  val rect_height: Int = (LENGTH * number_of_hexagons + 1) * RECTANGLE_HEIGHT_SCALE
  val xoffset: Double = 2 * rect_width + xoff
  var playerColor: Color = if (util.Random.nextBoolean()) BLUE else YELLOW
  var hexagons: Seq[Hexagon] = Seq()
  var ignoreInput = false
  display.addEventHandler(MouseEvent.MOUSE_PRESSED, new MouseEventHandler())
  start()

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
  }

  def draw() {
    gc.save()
    gc.setFill(YELLOW)
    gc.fillRect(0, 0, rect_width, rect_height)
    gc.fillRect(rect_width, rect_height, rect_width, rect_height)
    gc.setFill(BLUE)
    gc.fillRect(rect_width, 0, rect_width, rect_height)
    gc.fillRect(0, rect_height, rect_width, rect_height)
    gc.restore()
    for (hexagon <- hexagons) {
      hexagon.draw()
    }
  }

  def markPending(willMark: Boolean): Unit = {
    if (willMark) {
      var won: Option[Color] = None
      var marked = false
      val (x, y, clicked) = toMark
      hexagons.find(_.rect.contains(x, y)).foreach(h => {
        if (h.update(x, y, clicked, playerColor)) {
          h.mark(playerColor)
          marked = true
          won = solve(h.id)
        }
      })
      playerColor = if (marked) complementaryColor(playerColor) else playerColor
      draw()
      won match {
        case Some(color) => onWin(color)
        case None => ()
      }
    }
  }

  var toMark: (Double, Double, Boolean) = _

  class MouseEventHandler() extends EventHandler[MouseEvent] {
    override def handle(event: MouseEvent): Unit = {
      if (!ignoreInput) {
        val (x, y) = (event.getSceneX, event.getSceneY)
        val clicked = event.isPrimaryButtonDown || event.isSecondaryButtonDown
        toMark = (x, y, clicked)
        markAction()
      }
    }
  }

  private def solve(id: Int) = {
    val color = hexagons(id).color
    val chain = around(id, color, Seq())
    if (beginning(chain, color) && end(chain, color)) Some(color) else None
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
    else if (id >= number_of_hexagons * (number_of_hexagons - 1) && (id < number_of_hexagons * number_of_hexagons)) (false, false, false, true)
    //internal
    else (false, false, false, false)
  }

  def nameEdges(edges: (Boolean, Boolean, Boolean, Boolean)): String = {
    var str = ""
    if (edges._1) str += "blue_start, "
    if (edges._2) str += "blue_end, "
    if (edges._3) str += "yellow_start, "
    if (edges._4) str += "yellow_end, "
    if (str.isEmpty) "none " else str
  }

  lazy val bugCheck: String = hexagons.map(_.id).
    map(id => s"$id is member of edges ${nameEdges(edge(id))}and has neighbours: ${Neighbours(edge(id)).map(_ + id)}").mkString("\n")

  val Neighbours = Map((true, false, true, false) -> Seq(1, number_of_hexagons, number_of_hexagons + 1),
    (false, true, true, false) -> Seq(-1, number_of_hexagons, number_of_hexagons - 1),
    (true, false, false, true) -> Seq(1, -number_of_hexagons, -number_of_hexagons + 1),
    (false, true, false, true) -> Seq(-1, -number_of_hexagons, -number_of_hexagons - 1),
    (true, false, false, false) -> Seq(1, number_of_hexagons, number_of_hexagons + 1, -number_of_hexagons, -number_of_hexagons + 1),
    (false, true, false, false) -> Seq(-1, number_of_hexagons, number_of_hexagons - 1, -number_of_hexagons, -number_of_hexagons - 1),
    (false, false, true, false) -> Seq(1, -1, number_of_hexagons, number_of_hexagons - 1, number_of_hexagons + 1),
    (false, false, false, true) -> Seq(1, -1, -number_of_hexagons, -number_of_hexagons - 1, -number_of_hexagons + 1),
    (false, false, false, false) -> Seq(-1, +1, number_of_hexagons, -number_of_hexagons,
      number_of_hexagons + 1, number_of_hexagons - 1, -number_of_hexagons + 1, -number_of_hexagons - 1))

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
    case BLUE => chain.exists(c => hexagons(c).blue_start)
    case YELLOW => chain.exists(c => hexagons(c).yellow_start)
  }

  private def end(chain: Seq[Int], color: Color) = color match {
    case BLUE => chain.exists(c => hexagons(c).blue_end)
    case YELLOW => chain.exists(c => hexagons(c).yellow_end)
  }
}

class HexDisplay(questionDisplay: QuestionDisplay, width: Int, height: Int) extends Canvas(width, height) {

  class CloseDownTask extends Task[Unit] {
    override def call(): Unit = {
      Thread.sleep(5000)
      Platform.exit()
    }
  }

  import HexConstants._

  var (yellowScore, blueScore) = (0.0, 0.0)
  val table = Table(this, NUMBER_OF_HEXAGONS, 0, markAction, onWin)
  table.draw()
  setVisible(true)

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

  def update(score: Double): Unit = {
    val (currentYellowScore, currentBlueScore) = (yellowScore, blueScore)
    table.playerColor match {
      case YELLOW => yellowScore += score
      case BLUE => blueScore += score
    }
    table.markPending(blueScore > currentBlueScore || yellowScore > currentYellowScore)
    table.ignoreInput = false
  }

  private def clearScreen() = getGraphicsContext2D.clearRect(0, 0, getWidth, getHeight)

  def onWin(color: Color): Unit = {
    clearScreen()
    val winnerNLoser = color match {
      case YELLOW => (("Yellow", yellowScore), ("Blue", blueScore))
      case BLUE => (("Blue", blueScore), ("Yellow", yellowScore))
    }
    val winText = s"${winnerNLoser._1._1} player won with ${winnerNLoser._1._2} points."
    val loseText = s"Losing player ${winnerNLoser._2._1} scored ${winnerNLoser._2._1} points."
    val textLength = winText.length max loseText.length
    renderText(winText, textLength, -(getGraphicsContext2D.getFont.getSize + 5), color)
    renderText(loseText, textLength, getGraphicsContext2D.getFont.getSize + 5, complementaryColor(color))
  }

  def renderText(text: String, textLength: Int = -1, yOffset: Double = 0, color: Color = null, fontHeightMultiplier: Double = 1.0): Unit = {
    val gc = getGraphicsContext2D
    gc.save()
    gc.setFont(Font.font(gc.getFont.getFamily, FontWeight.BOLD, gc.getFont.getSize * fontHeightMultiplier))
    gc.setFill(color)
    gc.setStroke(color)
    val textDimension = gc.getFont.getSize
    val xOffset = textDimension * (if (textLength < 0) text.length else textLength) / 8
    val (xStart, yStart) = (getWidth / 2 - xOffset, getHeight / 2 + yOffset)
    gc.setTextAlign(TextAlignment.CENTER)
    gc.fillText(text, xStart, yStart)
    gc.restore()
  }
}

class MockHex(width: Int, height: Int) extends Canvas(width, height) {

  import HexConstants._

  val table = Table(this, NUMBER_OF_HEXAGONS, 0, () => println("mark action"), c => {
    getGraphicsContext2D.clearRect(0, 0, getWidth, getHeight)
    getGraphicsContext2D.strokeText(if (c == BLUE) "blue" else "yellow", getWidth / 2, getHeight / 2)
  })
  println()
  println(table.bugCheck)
  println()
  table.draw()
  setVisible(true)
}

