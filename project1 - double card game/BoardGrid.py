import turtle
from string import ascii_uppercase


class BoardGrid:
    def __init__(self, resolution_x, resolution_y, grid_size_x, grid_size_y):
        self.screensize_x = resolution_x
        self.screensize_y = resolution_y

        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y

        self.square_size = 50

        self.window = turtle.Screen()
        self.window.setup(resolution_x, resolution_y, 0, 0)
        self.window.setworldcoordinates(0, 0, self.screensize_x, self.screensize_y)

    def drawPiece(self, piece):
        piece_turtle = turtle.Turtle()
        piece_turtle.hideturtle()
        turtle.tracer(0, 0)

        piece_turtle.penup()
        piece_turtle.setpos((piece.red_pos_x+0.5)*self.square_size, (piece.red_pos_y+0.5)*self.square_size)
        piece_turtle.seth(piece.angle)
        piece_turtle.forward(self.square_size/2)
        piece_turtle.pendown()

        piece_turtle.fillcolor("red")
        piece_turtle.begin_fill()
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size/2)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size/2)
        piece_turtle.end_fill()

        piece_turtle.penup()
        piece_turtle.right(90)
        piece_turtle.back(self.square_size/2)
        piece_turtle.pendown()

        piece_turtle.fillcolor("black") if piece.side == 1 else piece_turtle.fillcolor("white")
        piece_turtle.begin_fill()
        piece_turtle.circle(5)
        piece_turtle.end_fill()

        piece_turtle.penup()
        piece_turtle.forward(self.square_size)
        piece_turtle.pendown()

        piece_turtle.fillcolor("black") if piece.side == 2 else piece_turtle.fillcolor("white")
        piece_turtle.begin_fill()
        piece_turtle.circle(5)
        piece_turtle.end_fill()

        piece_turtle.penup()
        piece_turtle.forward(self.square_size/2)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size/2)
        piece_turtle.left(90)
        piece_turtle.color("green")
        piece_turtle.width("3")
        piece_turtle.pendown()

        piece_turtle.forward(self.square_size*2)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size*2)
        piece_turtle.left(90)
        piece_turtle.forward(self.square_size)
        turtle.update()

    def drawBoard(self):
        grid_turtle = turtle.Turtle()
        grid_turtle.hideturtle()
        turtle.tracer(0, 0)

        for index in range(0, self.grid_size_x):
            grid_turtle.forward(self.square_size)
            grid_turtle.goto(grid_turtle.xcor(), self.square_size*(self.grid_size_y+1))
            grid_turtle.sety(0)
            grid_turtle.write(ascii_uppercase[index], font=("Arial", 32, "normal"))
        grid_turtle.forward(self.square_size)
        grid_turtle.goto(grid_turtle.xcor(), self.square_size*(self.grid_size_y+1))

        grid_turtle.penup()
        grid_turtle.setpos(0, 0)
        grid_turtle.left(90)
        grid_turtle.pendown()

        for index in range(0, self.grid_size_y):
            grid_turtle.forward(self.square_size)
            grid_turtle.goto(self.square_size*(self.grid_size_x+1), grid_turtle.ycor())
            grid_turtle.setx(0)
            grid_turtle.write(index+1, font=("Arial", 32, "normal"))
        grid_turtle.forward(self.square_size)
        grid_turtle.goto(self.square_size*(self.grid_size_x+1), grid_turtle.ycor())
        turtle.update()

    def refresh(self, pieces):
        self.window.clear()
        self.drawBoard()
        for piece in pieces:
            self.drawPiece(piece)

    def closeBoard(self):
        self.window.exitonclick()
