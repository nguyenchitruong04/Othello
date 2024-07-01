import pygame
import sys
import copy
import os

# Khởi tạo Pygame
pygame.init()

# Kích thước màn hình và ô
screen_width = 1080
screen_height = 800
grid_size = 8
cell_size = screen_height // (grid_size + 2)  # +2 để thêm lề cho chỉ số hàng và cột

# Tạo cửa sổ
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Othello Game")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Khởi tạo bàn cờ
def init_board():
    board = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    board[3][3] = WHITE
    board[4][4] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    return board

board = init_board()

# Người chơi hiện tại (Đen đi trước)
current_player = BLACK

# Thêm hàm để vẽ bảng lưới và các quân cờ
def draw_board(black_count, white_count):
    pygame.draw.rect(screen, BROWN, (0, 0, screen_width, screen_height))

    for row in range(grid_size):
        for col in range(grid_size):
            rect = pygame.Rect((col + 1) * cell_size, (row + 1) * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, GREEN, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

    font = pygame.font.SysFont(None, 24)
    for i in range(grid_size):
        row_text = font.render(str(i + 1), True, WHITE)
        screen.blit(row_text,
                    ((0.5) * cell_size - row_text.get_width() // 2, (i + 1.5) * cell_size - row_text.get_height() // 2))

        col_text = font.render(chr(65 + i), True, WHITE)
        screen.blit(col_text,
                    ((i + 1.5) * cell_size - col_text.get_width() // 2, (0.5) * cell_size - col_text.get_height() // 2))

    font = pygame.font.Font(None, 36)
    black = font.render(f"Black: {black_count} ", True, WHITE)
    white = font.render(f"White: {white_count}", True, WHITE)
    screen.blit(black, (800, 100))
    screen.blit(white, (800, 200))

    valid_moves = get_valid_moves(board, current_player)
    for move in valid_moves:
        row, col = move
        center_x = (col + 1.5) * cell_size
        center_y = (row + 1.5) * cell_size
        pygame.draw.circle(screen, BLACK, (center_x, center_y), cell_size // 2 - 5, 2)

def draw_pieces():
    radius = cell_size // 2 - 5
    for row in range(grid_size):
        for col in range(grid_size):
            if board[row][col] is not None:
                center_x = (col + 1.5) * cell_size
                center_y = (row + 1.5) * cell_size
                pygame.draw.circle(screen, board[row][col], (center_x, center_y), radius)

def is_valid_move(board, row, col, player):
    if board[row][col] is not None:
        return False

    opponent = WHITE if player == BLACK else BLACK
    valid = False

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == opponent:
            while 0 <= r < grid_size and 0 <= c < grid_size:
                r += dr
                c += dc
                if not (0 <= r < grid_size and 0 <= c < grid_size):
                    break
                if board[r][c] is None:
                    break
                if board[r][c] == player:
                    valid = True
                    break

    return valid

def place_piece(board, row, col, player):
    opponent = WHITE if player == BLACK else BLACK
    board[row][col] = player

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        pieces_to_flip = []
        while 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == opponent:
            pieces_to_flip.append((r, c))
            r += dr
            c += dc
        if 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == player:
            for rr, cc in pieces_to_flip:
                board[rr][cc] = player

def count_pieces(board):
    black_count = sum(row.count(BLACK) for row in board)
    white_count = sum(row.count(WHITE) for row in board)
    return black_count, white_count

def is_game_over(board):
    black_count, white_count = count_pieces(board)
    if black_count == 0 or white_count == 0:
        return True
    for row in range(grid_size):
        for col in range(grid_size):
            if is_valid_move(board, row, col, BLACK) or is_valid_move(board, row, col, WHITE):
                return False
    return True

def has_valid_move(board, player):
    for row in range(grid_size):
        for col in range(grid_size):
            if is_valid_move(board, row, col, player):
                return True
    return False

def get_valid_moves(board, player):
    valid_moves = []
    for row in range(grid_size):
        for col in range(grid_size):
            if is_valid_move(board, row, col, player):
                valid_moves.append((row, col))
    return valid_moves

def othello(black_count, white_count):
    draw_board(black_count, white_count)
    draw_pieces()

def display_winner():
    black_count, white_count = count_pieces(board)
    if black_count > white_count:
        print("Black wins!")
        a = "Black wins!"
    elif white_count > black_count:
        print("White wins!")
        a = "white wins!"
    else:
        print("It's a tie!")
        a = "It's a tie!"

    return a

class ComputerPlayer:
    def __init__(self, grid, difficulty='easy'):
        self.grid = grid
        self.difficulty = difficulty
        self.depth = 2 if difficulty == 'easy' else 5  # Độ sâu cho độ khó

    def evaluate_board(self, board, player):
        black_count, white_count = count_pieces(board)
        return black_count - white_count if player == BLACK else white_count - black_count

    def computer_hard(self, grid, depth, alpha, beta, player):
        if depth == 0 or is_game_over(grid):
            return None, self.evaluate_board(grid, player)
        
        best_move = None

        if player == BLACK:
            max_eval = -float('inf')
            for move in get_valid_moves(grid, player):
                temp_grid = copy.deepcopy(grid)
                place_piece(temp_grid, move[0], move[1], player)
                _, current_eval = self.computer_hard(temp_grid, depth - 1, alpha, beta, WHITE)
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = move
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for move in get_valid_moves(grid, player):
                temp_grid = copy.deepcopy(grid)
                place_piece(temp_grid, move[0], move[1], player)
                _, current_eval = self.computer_hard(temp_grid, depth - 1, alpha, beta, BLACK)
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_move = move
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
            return best_move, min_eval

    def get_move(self):
        return self.computer_hard(self.grid, self.depth, -float('inf'), float('inf'), current_player)[0]

# Hiển thị menu
def display_menu():

    while True:
        screen.fill(BROWN)
        font = pygame.font.Font(None, 74)
        text = font.render("Choose Difficulty", True, WHITE)
        screen.blit(text, (400, 100))

        easy_button = pygame.Rect(450, 250, 200, 100)
        hard_button = pygame.Rect(450, 400, 200, 100)
        pygame.draw.rect(screen, BROWN, easy_button)
        pygame.draw.rect(screen, BROWN, hard_button)

        font = pygame.font.Font(None, 50)
        easy_text = font.render("EASY", True, "green")
        hard_text = font.render("HARD", True, "red")
        screen.blit(easy_text, (520, 270))
        screen.blit(hard_text, (510, 420))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    return 'easy'
                elif hard_button.collidepoint(event.pos):
                    return 'hard'


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)
font = pygame.font.SysFont(None, 55)
def main_menu(font):
    run = True

    while run:
        screen.fill(BROWN)
        draw_text("Main Menu", font, "black", screen, 400, 50)
        mouse = pygame.mouse.get_pos()
        o = pygame.draw.rect(screen, BROWN, (400, 300, screen_width / 5, screen_height / 12))
        draw_text("Play Game", font, "black", screen, o.x, o.centery - 20)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if o.collidepoint(event.pos[0], event.pos[1]):
                    return display_menu()
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
    pygame.display.flip()

def win(text):

        wait = True
        while wait:
            screen.fill(BROWN)
            draw_text(text, font, "black", screen, 300, 50)
            draw_text(f"Black: {black_count} - White: {white_count}", font, "black", screen, 300, 150)
            mouse = pygame.mouse.get_pos()
            o = pygame.draw.rect(screen, BROWN, (500, 300, 100, 50))
            draw_text("Exit", font, "black", screen, o.x, o.centery - 20)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if o.collidepoint(event.pos[0], event.pos[1]):
                        wait = False
                        sys.exit()

                if event.type == pygame.QUIT:
                    sys.exit()

        pygame.display.flip()

def reset_game():
    global board, current_player, computer_player
    board = init_board()
    current_player = BLACK
    difficulty = display_menu()
    computer_player = ComputerPlayer(board, difficulty)
    draw_board(black_count, white_count)
    draw_pieces()

# Chọn độ khó
difficulty = main_menu(font)

# Tạo đối tượng ComputerPlayer(người chơi máy) với độ khó đã chọn
computer_player = ComputerPlayer(board, difficulty)
global run
run = True
# Vòng lặp chính của trò chơi
while run == True :
    black_count, white_count = count_pieces(board)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            col, row = x // cell_size - 1, y // cell_size - 1
            if 0 <= row < grid_size and 0 <= col < grid_size and is_valid_move(board, row, col, current_player):
                place_piece(board, row, col, current_player)
                current_player = WHITE if current_player == BLACK else BLACK
                black_count, white_count = count_pieces(board)

    if not has_valid_move(board, current_player):
        current_player = WHITE if current_player == BLACK else BLACK
        if not has_valid_move(board, current_player):
            break

    if current_player == WHITE:
        move = computer_player.get_move()
        if move:
            place_piece(board, move[0], move[1], WHITE)
            current_player = BLACK
    if is_game_over(board) == True :
        print("Game Over")


    screen.fill(BLACK)
    othello(black_count, white_count)
    pygame.display.flip()

win(display_winner())
pygame.display.flip()




