import random
import tkinter

colorsList = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Brown', 'Black', 'Pink', 'Grey', 'White']
score = 0
seconds = int(31)


def gameplay(event):
  global seconds

  if seconds == 31:
    timecount()

  changeColor()


def timecount():
    global timeRemaining, scoreLabel, seconds, score, userInput
  
    if seconds > 0:
        seconds -= 1
        timeRemaining.config(text = "Time: " + str(seconds))
        timeRemaining.after(1000, timecount)
    else:
        timeRemaining.config(text = "Time's up!\nYour score is " + str(score) + ".", font = ('Comic Sans MS', 20))
        label.after(0, label.destroy)
        scoreLabel.after(0, scoreLabel.destroy)
        colorGuess.after(0, colorGuess.destroy)


def changeColor():
  global seconds, score

  if seconds > 0:
    if colorGuess.get().lower() == colorsList[0].lower():
        score += 1

    colorGuess.focus_set()
    colorGuess.delete(0, tkinter.END)

    random.shuffle(colorsList)

    label.config(fg = str(colorsList[0]), text = str(colorsList[1]))
    scoreLabel.config(text = "Score: " + str(score))


game = tkinter.Tk()
game.title("Guess the Color, Not the Word!")
game.geometry("400x200")

userInput = tkinter.Entry(game)

timeRemaining = tkinter.Label(game, text = "Time remaining: " + str(seconds), font = ('Comic Sans MS', 12))
timeRemaining.pack()

scoreLabel = tkinter.Label(game, text = "Press enter to start", font = ('Comic Sans MS', 12))
scoreLabel.pack()

label = tkinter.Label(game, font = ('Comic Sans MS', 60))
label.pack()

colorGuess = tkinter.Entry(game)
colorGuess.pack()
colorGuess.focus_set()

game.bind('<Return>', gameplay)
game.mainloop()