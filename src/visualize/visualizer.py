"""
Module to visualize/replay a game of snake.
Relatively poorly done, as it was a quick set up via pygame...
"""

import zlib
import pickle
import base64
import pygame


def visualize(game_data):
    """
    Visualizes a previously played game of snake given its recorded game data.
    """

    def decompress_b64_to_list(b64_string):
        compressed = base64.b64decode(b64_string)
        return pickle.loads(zlib.decompress(compressed))

    solver_name = game_data['solver_name']
    solver_type = game_data['solver_type']
    move_history = decompress_b64_to_list(game_data["move_history"])
    apple_history = decompress_b64_to_list(game_data["apple_history"])

    width, height = game_data["grid_size"]

    def index_to_pos(index):
        return (index % width, index // width)

    initial_snake = [index_to_pos(i) for i in game_data["initial_snake"]]
    move_history = [index_to_pos(i) for i in move_history]
    apple_history = [index_to_pos(i) for i in apple_history]

    CELL_SIZE = 30
    FPS = 30
    MARGIN = 6  # amount of margin inside each cell
    SNAKE_COLOR = (0, 255, 0)
    INFO_PANEL_WIDTH = 300
    FPS = 10

    pygame.init()
    screen = pygame.display.set_mode((width * CELL_SIZE + INFO_PANEL_WIDTH, height * CELL_SIZE))
    clock = pygame.time.Clock()

    pygame.font.init()
    font = pygame.font.SysFont("Arial", 18)

    def draw_board(snake, apple, move_num):
        screen.fill((0, 0, 0))  # Clear screen ONCE

        draw_snake(snake)
        draw_apple(apple)
        draw_info_panel(move_num, len(set(snake)))

        pygame.display.flip()

    def draw_apple(apple):
        # Apple
        APPLE_MARGIN = 6
        ax = apple[0] * CELL_SIZE + APPLE_MARGIN // 2
        ay = apple[1] * CELL_SIZE + APPLE_MARGIN // 2
        asize = CELL_SIZE - APPLE_MARGIN
        pygame.draw.rect(screen, (255, 0, 0), (ax, ay, asize, asize))

    def draw_snake(snake):
        HEAD_RADIUS = 0
        for i in range(len(snake)):
            if i == len(snake)-1:
                HEAD_RADIUS = size // 3
            
            x, y = snake[i]
            rect_x = x * CELL_SIZE + MARGIN // 2
            rect_y = y * CELL_SIZE + MARGIN // 2
            size = CELL_SIZE - MARGIN
            pygame.draw.rect(screen, SNAKE_COLOR, (rect_x, rect_y, size, size), border_radius=HEAD_RADIUS)

            # Draw connector to the previous segment
            if i > 0:
                px, py = snake[i - 1]
                dx = x - px
                dy = y - py

                if dx != 0:  # horizontal connection
                    min_x = min(x, px) * CELL_SIZE + (CELL_SIZE - MARGIN) // 2
                    connector = pygame.Rect(min_x, rect_y, CELL_SIZE, size)
                elif dy != 0:  # vertical connection
                    min_y = min(y, py) * CELL_SIZE + (CELL_SIZE - MARGIN) // 2
                    connector = pygame.Rect(rect_x, min_y, size, CELL_SIZE)
                pygame.draw.rect(screen, SNAKE_COLOR, connector)

    def draw_info_panel(move_num, score):
        panel_x = width * CELL_SIZE
        panel_rect = pygame.Rect(panel_x, 0, INFO_PANEL_WIDTH, height * CELL_SIZE)
        pygame.draw.rect(screen, (30, 30, 30), panel_rect)

        lines = [
            f"Move: {move_num}/{game_data['total_moves']}",
            f"Solver: {solver_name} ({solver_type})",
            f"Score: {score}",
            f"FPS: {FPS}",
        ]

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (panel_x + 10, 20 + i * 30))


    def adjust_fps(fps, direction):
        if direction == 'up':
            increment = max(1, fps // 5)  # The larger the FPS, the bigger the increment
            return min(2000, fps + increment)  # Limit the max FPS to 1000
        elif direction == 'down':
            decrement = max(1, fps // 5)  # The larger the FPS, the bigger the decrement
            return max(1, fps - decrement)  # Limit the min FPS to 1
        return fps

    def get_next_game_state(snake, apple_index, move_num, reverse=False):
        if not reverse:
            if move_num >= len(move_history)-1:
                apple = (-1, -1)
                return snake, apple, apple_index, move_num

            move_num += 1
            move = move_history[move_num]
            snake.append(move)

            if move == apple_history[apple_index]:
                apple_index += 1
            else:
                last_deleted_snake = snake.pop(0)

            if apple_index >= len(apple_history):
                apple = (-1, -1)
            else:
                apple = apple_history[apple_index]

            return snake, apple, apple_index, move_num
        else:
            if move_num == -1:
                apple = apple_history[apple_index]
                return snake, apple, apple_index, move_num

            if snake[-1] == apple_history[apple_index-1]:
                apple_index -= 1
                last_deleted_snake = []
            else:
                if move_num > 2:
                    last_deleted_snake = [move_history[move_num - len(snake)]]
                else:
                    last_deleted_snake = [initial_snake[move_num]]


            apple = apple_history[apple_index]
            move_num -= 1
            snake = last_deleted_snake + snake[:-1]

            return snake, apple, apple_index, move_num


    pygame.display.set_caption(f"Snake Replay")

    paused = False
    apple_index = 0
    snake = initial_snake[:]
    move_num = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        FPS = adjust_fps(FPS, 'up')
                    
                    elif event.key == pygame.K_DOWN:
                        FPS = adjust_fps(FPS, 'down')
                    
                    elif event.key == pygame.K_RIGHT:
                        paused = True
                        snake, apple, apple_index, move_num = get_next_game_state(snake, apple_index, move_num)

                    elif event.key == pygame.K_LEFT:
                        paused = True
                        snake, apple, apple_index, move_num = get_next_game_state(snake, apple_index, move_num, reverse=True)

        if not paused:
            snake, apple, apple_index, move_num = get_next_game_state(snake, apple_index, move_num)

        draw_board(snake, apple, move_num+1)
        clock.tick(FPS)