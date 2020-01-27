from artboard import Artboard, Yarn
n = 90

# 12 in. diameter
board = Artboard(304.8, n)
# for i in range(0, n):
    # board.add_string(i, (i + 15) % n)
# board.add_string(0, 1)
for j in range(0, n):
	for i in range(j, n):
		board.add_string(j, i)

print(f"Total Length (ft.): {board.total_length()} ")


print(board.render(background='#FFFFFF').savePng('build/test.png'))