import random
import pygame
from pygame.locals import *

# CONSTANTS
board_size = 3
board_width = board_size
board_height = board_size
tile_size = int(100 / + ((board_height + board_width) * 0.1))
window_width = 1080
window_height = 720

# COLORS
black = (0, 0, 0)
white = (255, 255, 255)
dark_turquoise = (80, 54, 73)
green = (0, 204, 0)
purple = (132, 94, 194)

# SYSTEM COLOR
message_color = white
bg_colors = black
tile_color = white
text_color = white
border_color = purple
basic_font_size = int(tile_size / 2)
message_font_size = 50

# PYGAME INIT FUNCTION
pygame.init()
pygame.display.set_caption('Puzzle')
screen = pygame.display.set_mode((window_width, window_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
screen.fill(bg_colors)
pygame.display.flip()

# GAME CONSTANTS
basic_font = pygame.font.Font('Data/Font/MatchupPro.ttf', basic_font_size)
message_font = pygame.font.Font('Data/Font/MatchupPro.ttf', message_font_size)
blank = int()
TOP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
x_margin = int((window_width - (tile_size * board_width + (board_width - 1))) / 2)
y_margin = int((window_height - (tile_size * board_height + (board_height - 1))) / 2)
bubble_sprite = pygame.image.load("Data/AnimationBubble/Opening/1.png")
main_board = []
animation_speed = 100
frame_rate = 30
animating = False
generating = False


class Button:
    def __init__(self, sprite, size, rect, command):
        self.rect = pygame.Rect(rect, size)
        self.image = pygame.image.load(sprite)
        self.image_size = pygame.transform.scale(self.image, size)
        self.command = command

    def render(self, screen):
        screen.blit(self.image_size, self.rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.command()


reset_button = Button(f"Data/Sprite/tile009.png", (128, 128), (870, 345), lambda: generate_new_puzzle(10 * board_size))
quit_button = Button(f"Data/Sprite/tile022.png", (128, 128), (870, 505), lambda: exit())


def render(s):
    reset_button.render(s)
    quit_button.render(s)
    if generating:
        screen.blit(bubble_sprite, (870, 200))


def main():
    global screen, animating, main_board
    generate_new_puzzle(10 * board_size)
    solved_board = create_board()
    all_moves = []

    while True:
        msg = 'PRESS ARROW keys to slide.'
        if main_board == solved_board:
            msg = 'You solved the puzzle GG!'
        draw_board(main_board, msg)
        slide_to = None
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                reset_button.get_event(event)
                quit_button.get_event(event)
            if event.type == pygame.QUIT:
                exit()
            if event.type == KEYUP:
                if event.key == K_LEFT and is_valid_move(main_board, LEFT) and not animating:
                    slide_to = LEFT
                elif event.key == K_RIGHT and is_valid_move(main_board, RIGHT) and not animating:
                    slide_to = RIGHT
                elif event.key == K_UP and is_valid_move(main_board, TOP) and not animating:
                    slide_to = TOP
                elif event.key == K_DOWN and is_valid_move(main_board, DOWN) and not animating:
                    slide_to = DOWN
            if slide_to:
                render(screen)
                animating = True
                animate_move(main_board, slide_to)
                all_moves.append(slide_to)
        render(screen)
        pygame.display.update()


def animate_move(board, move):
    x_blank, y_blank = get_blank_position(board)

    make_move(board, move)
    if move == TOP:
        animate_tile(board, x_blank, y_blank, x_blank, y_blank + 1)
    elif move == DOWN:
        animate_tile(board, x_blank, y_blank, x_blank, y_blank - 1)
    elif move == LEFT:
        animate_tile(board, x_blank, y_blank, x_blank + 1, y_blank)
    elif move == RIGHT:
        animate_tile(board, x_blank, y_blank, x_blank - 1, y_blank)


def animate_tile(board, end_x, end_y, start_x, start_y):
    global animating, animation_speed
    animation_offset = 30
    start_pos = (x_margin + start_x * tile_size + start_x, y_margin + start_y * tile_size + start_y)
    end_pos = (x_margin + end_x * tile_size + end_x, y_margin + end_y * tile_size + end_y)
    speed = animation_speed / frame_rate
    tile_surface = create_tile_surface(board[end_x][end_y], animation_offset)
    for i in range(frame_rate):
        x_offset = int((end_pos[0] - start_pos[0]) / frame_rate * i)
        y_offset = int((end_pos[1] - start_pos[1]) / frame_rate * i)
        screen.blit(tile_surface, (start_pos[0] + (x_offset + (animation_offset/2)), start_pos[1] + (y_offset + (animation_offset/2))))
        pygame.display.update()
        pygame.time.wait(int(speed))
        screen.fill(bg_colors, (start_pos[0], start_pos[1], tile_size, tile_size))
    animating = False


def create_tile_surface(tile_num, offset):
    image = pygame.image.load("Data/Sprite/tile006.png")
    image_size = pygame.transform.scale(image, ((tile_size - offset), (tile_size - offset)))
    text = basic_font.render(str(tile_num), False, text_color)
    text_rect = text.get_rect()
    text_rect.center = ((tile_size - offset) / 2, ((tile_size - offset) / 2) - 22)
    image_size.blit(text, text_rect)
    return image_size


def create_board():
    buffer = 1
    board = []
    for x in range(board_width):
        column = []
        for y in range(board_height):
            column.append(buffer)
            buffer += board_width
        board.append(column)
        buffer -= board_width * (board_height - 1) + (board_width - 1)
    board[board_width - 1][board_height - 1] = blank
    return board


def get_blank_position(board):
    for x in range(board_width):
        for y in range(board_height):
            if board[x][y] == blank:
                return x, y


def make_move(board, move):
    x_blank, y_blank = get_blank_position(board)

    if move == TOP:
        board[x_blank][y_blank], board[x_blank][y_blank + 1] = board[x_blank][y_blank + 1], board[x_blank][y_blank]
    elif move == DOWN:
        board[x_blank][y_blank], board[x_blank][y_blank - 1] = board[x_blank][y_blank - 1], board[x_blank][y_blank]
    elif move == LEFT:
        board[x_blank][y_blank], board[x_blank + 1][y_blank] = board[x_blank + 1][y_blank], board[x_blank][y_blank]
    elif move == RIGHT:
        board[x_blank][y_blank], board[x_blank - 1][y_blank] = board[x_blank - 1][y_blank], board[x_blank][y_blank]


def get_random_move(board, last_move=None):
    valid_moves = [TOP, DOWN, LEFT, RIGHT]

    if last_move == TOP or not is_valid_move(board, DOWN):
        valid_moves.remove(DOWN)
    if last_move == DOWN or not is_valid_move(board, TOP):
        valid_moves.remove(TOP)
    if last_move == LEFT or not is_valid_move(board, RIGHT):
        valid_moves.remove(RIGHT)
    if last_move == RIGHT or not is_valid_move(board, LEFT):
        valid_moves.remove(LEFT)

    return random.choice(valid_moves)


def is_valid_move(board, move):
    x_blank, y_blank = get_blank_position(board)
    return (move == TOP and y_blank != len(board[0]) - 1) or \
        (move == DOWN and y_blank != 0) or \
        (move == LEFT and x_blank != len(board) - 1) or \
        (move == RIGHT and x_blank != 0)


def get_left_top_tile(tile_x, tile_y):
    left = x_margin + (tile_x * tile_size) + (tile_x - 1)
    top = y_margin + (tile_y * tile_size) + (tile_y - 1)
    return left, top


def make_text(text, color, bg_color, top, left):
    text_surf = message_font.render(text, True, color, bg_color)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (top, left)
    return text_surf, text_rect


def draw_tile(tile_x, tile_y, number, adj_x=0, adj_y=-22):
    left, top = get_left_top_tile(tile_x, tile_y)
    image = pygame.image.load("Data/Sprite/tile006.png")
    image_size = pygame.transform.scale(image, (tile_size, tile_size))
    text_surf = basic_font.render(str(number), True, text_color)
    text_rect = text_surf.get_rect()
    text_rect.center = left + int(tile_size / 2) + adj_x, top + int(tile_size / 2) + adj_y
    screen.blit(image_size, (left, top, tile_size, tile_size))
    screen.blit(text_surf, text_rect)


def draw_board(board, message):
    screen.fill(bg_colors)
    if message:
        text_surf, text_rect = make_text(message, message_color, bg_colors, (window_width/2) - (len(message) * 9.5), 35)
        screen.blit(text_surf, text_rect)

    for tile_x in range(len(board)):
        for tile_y in range(len(board[0])):
            if board[tile_x][tile_y]:
                draw_tile(tile_x, tile_y, board[tile_x][tile_y])

    left, top = get_left_top_tile(0, 0)
    width = board_width * tile_size
    height = board_height * tile_size
    pygame.draw.rect(screen, border_color, (left - 15, top - 15, width + (board_width + 30),
                                            height + (board_height + 30)), 8)


def generate_new_puzzle(num_slides):
    global animation_speed, main_board, generating
    v = 0
    generating = True
    spawn_bubble()
    animation_speed = 1
    board = create_board()
    pygame.display.update()
    last_move = None
    for i in range(num_slides):
        if v > 2:
            v = 0
        v += 1
        wait_bubble(v)
        render(screen)
        move = get_random_move(board, last_move)
        animate_move(board, move)
        draw_board(board, "Generating...")
        last_move = move
    animation_speed = 100
    generating = False
    main_board = board


def spawn_bubble():
    global bubble_sprite
    for i in range(1, 7):
        pygame.display.update()
        bubble_sprite_no = pygame.image.load("Data/AnimationBubble/Opening/" + str(i) + ".png")
        bubble_sprite_sized = pygame.transform.scale(bubble_sprite_no, (128, 128))
        bubble_sprite = bubble_sprite_sized
        render(screen)
        pygame.time.wait(50)


def wait_bubble(v):
    global bubble_sprite
    bubble_sprite_no = pygame.image.load("Data/AnimationBubble/Waiting/" + str(v) + ".png")
    bubble_sprite_sized = pygame.transform.scale(bubble_sprite_no, (128, 128))
    bubble_sprite = bubble_sprite_sized
    render(screen)


if __name__ == '__main__':
    main()