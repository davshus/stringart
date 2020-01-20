from artboard import Artboard, Yarn
n = 180
board = Artboard(304.8, n)
for i in range(0, n):
    board.add_string(0, i)
# board.add_string(0, 45)
print(board.render(background='#FFFFFF').savePng('build/test.png'))