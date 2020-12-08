import pygame
import time
# import random

pygame.font.init()
window = pygame.display.set_mode((500, 600))
font_one = pygame.font.SysFont("arial", 20)
font_two = pygame.font.SysFont("arial", 30)


def initialize_timer(secs):
    s = secs % 60
    m = secs // 60
    h = m // 60

    return "{}:{}:{}".format(str(h), str(m), str(s))


def initialize_window(screen, board, timer, strikes):
    screen.fill((255, 255, 255))
    txt = font_one.render(initialize_timer(timer), 1, (0, 0, 0))
    window.blit(txt, (400, 520))
    text_one = font_two.render("R = Reset Board | S = Solve Board | X = Exit Game", 1, (0, 0, 0))
    window.blit(text_one, (20, 520))
    txt = font_one.render("X " * strikes, 1, (255, 0, 0))
    window.blit(txt, (10, 570))
    txt = font_one.render("Strikes:{}".format(strikes), 1, (255, 0, 0))
    window.blit(txt, (250, 550))
    board.draw()


def verify(board, num, position):
    space_x = position[1] // 3
    space_y = position[0] // 3

    for i in range(space_y * 3, space_y * 3 + 3):
        for j in range(space_x * 3, space_x * 3 + 3):
            if board[i][j] == num and (i, j) != position:
                return False
    # Verify row works
    for i in range(len(board[0])):
        if board[position[0]][i] == num and position[1] != i:
            return False
    # Verify column works
    for i in range(len(board)):
        if board[i][position[1]] == num and position[0] != i:
            return False

    # If we make it through, return True
    return True


def find_open_squares(board):
    for rows in range(len(board)):
        for cols in range(len(board[0])):
            if board[rows][cols] == 0:
                return rows, cols


class Board:
    board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]

    def __init__(self, rows, cols, width, height, screen):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.screen = screen
        self.model = None
        self.selected = None
        self.squares = [[Squares(i, j, width, height, self.board[i][j]) for j in range(cols)] for i in range(rows)]
        self.refresh()

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].selected = False

        self.squares[row][col].selected = True
        self.selected = (row, col)

    def choose(self, pos):
        gap = self.width / 9
        x = pos[0] // gap
        y = pos[1] // gap
        z = (int(y), int(x))
        if pos[0] < self.width and pos[1] < self.height:
            return z
        else:
            return None

    def delete(self):
        row, col = self.selected
        if self.squares[row][col].num == 0:
            self.squares[row][col].sub(0)

    def refresh(self):
        self.model = [[self.squares[i][j].num for j in range(self.cols)] for i in range(self.rows)]

    def position(self, val):
        row, col = self.selected
        if self.squares[row][col].num == 0:
            self.squares[row][col].set(val)
            self.refresh()

            if verify(self.model, val, (row, col)) and self.solve():
                return True
            else:
                self.squares[row][col].set(0)
                self.squares[row][col].sub(0)
                self.refresh()
                return False

    def draw(self):
        # Draw Grid Lines
        space = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                line_width = 2
            else:
                line_width = 1
            pygame.draw.line(self.screen, (0, 0, 0), (0, i * space), (self.width, i * space), line_width)
            pygame.draw.line(self.screen, (0, 0, 0), (i * space, 0), (i * space, self.height), line_width)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].draw(self.screen)

    def mock_up(self, val):
        row, col = self.selected
        self.squares[row][col].sub(val)

    def solve(self):
        find = find_open_squares(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if verify(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0

        return False

    def backtrack(self):
        self.refresh()
        found = find_open_squares(self.model)
        if not found:
            return True
        else:
            row, col = found

        for i in range(1, 10):
            if verify(self.model, i, (row, col)):
                self.model[row][col] = i
                self.squares[row][col].set(i)
                self.squares[row][col].visualize(self.screen, True)
                self.refresh()
                pygame.display.update()
                pygame.time.delay(100)

                if self.backtrack():
                    return True

                self.model[row][col] = 0
                self.squares[row][col].set(0)
                self.refresh()
                self.squares[row][col].visualize(self.screen, False)
                pygame.display.update()
                pygame.time.delay(100)

        return False

    def verify_completion(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.squares[i][j].num == 0:
                    return False
        return True


class Squares:
    rows = 9
    cols = 9

    def __init__(self, row, col, width, height, num):
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.num = num
        self.selected = False

    def set(self, num):
        self.num = num

    def sub(self, num):
        self.temp = num

    def draw(self, win):
        space = self.width / 9
        x_coord = self.col * space
        y_coord = self.row * space

        if self.temp != 0 and self.num == 0:
            text = font_one.render(str(self.temp), 1, (0, 128, 128))
            win.blit(text, (x_coord+5, y_coord+5))
        elif not(self.num == 0):
            text = font_one.render(str(self.num), 1, (0, 0, 0))
            win.blit(text, (x_coord + (space/2 - text.get_width()/2), y_coord + (space/2 - text.get_height()/2)))

        if self.selected:
            pygame.draw.rect(win, (0, 128, 128), (x_coord, y_coord, space, space), 3)

    def visualize(self, win, boo=True):
        space = self.width / 9
        x_coord = self.col * space
        y_coord = self.row * space

        pygame.draw.rect(win, (255, 255, 255), (x_coord, y_coord, space, space), 0)

        text = font_two.render(str(self.num), 1, (0, 0, 0))
        win.blit(text, (x_coord + (space / 2 - text.get_width() / 2), y_coord + (space / 2 - text.get_height() / 2)))
        if boo:
            pygame.draw.rect(win, (0, 255, 255), (x_coord, y_coord, space, space), 3)
        else:
            pygame.draw.rect(win, (0, 0, 255), (x_coord, y_coord, space, space), 3)


def main():
    board = Board(9, 9, 500, 500, window)
    start = time.time()
    strikes = 0
    play = True
    key = None

    while play:
        play_timer = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_r:
                    # If R is pressed reset the board
                    main()
                if event.key == pygame.K_s:
                    board.backtrack()
                if event.key == pygame.K_x:
                    play = False
                if event.key == pygame.K_DELETE:
                    board.delete()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.squares[i][j].temp != 0:
                        if board.position(board.squares[i][j].temp):
                            txt = font_one.render("Correct! Strikes:{}".format(strikes), 1, (0, 255, 0))
                            window.blit(txt, (250, 570))
                        else:
                            strikes += 1
                            if strikes == 5 and not(board.verify_completion()):
                                txt = font_one.render("Game Over", 1, (0, 0, 0))
                                window.blit(txt, (250, 570))
                                play = False
                    key = None
                    if board.verify_completion():
                        txt_two = font_one.render("Congrats, Board Completed!", 1, (0, 0, 0))
                        window.blit(txt_two, (20, 570))
                        pygame.time.delay(3000)
                        play = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                valid = board.choose(pos)
                if valid:
                    board.select(valid[0], valid[1])
                    key = None

        if board.selected and key is not None:
            board.mock_up(key)

        initialize_window(window, board, play_timer, strikes)
        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit()
