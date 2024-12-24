import pygame
import random
import os
import asyncio

pygame.init()

BOX_SIZE = 32
SCREEN_WIDTH = ((pygame.display.Info().current_w // BOX_SIZE) - 1) * BOX_SIZE
SCREEN_HEIGHT = ((pygame.display.Info().current_h // BOX_SIZE) - 1) * BOX_SIZE
GRID_WIDTH = SCREEN_WIDTH // BOX_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BOX_SIZE

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2, GRID_HEIGHT // 2 + 1)]
        self.direction = (0, -1)
        self.grow = False
        asyncio.sleep(1)

    def move(self):
        head_x, head_y = self.positions[0]
        direction_x, direction_y = self.direction
        new_head_position = (head_x + direction_x, head_y + direction_y)

        if new_head_position[0] < 0 or new_head_position[0] >= GRID_WIDTH or new_head_position[1] < 0 or new_head_position[1] >= GRID_HEIGHT:
            raise ValueError("L bozo bro hit the edge")

        if new_head_position in self.positions:
            raise ValueError("L bozo bro hit himself")

        self.positions = [new_head_position] + self.positions[:-1]
        if self.grow:
            self.positions.append(self.positions[-1])
            self.grow = False

    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def grow_snake(self):
        self.grow = True

    def draw(self, surface):
        for index, position in enumerate(self.positions):
            color_intensity = 100 - (index * 10) if 100 - (index * 10) > 0 else 0
            color = (255, color_intensity, color_intensity)
            rect = pygame.Rect(position[0] * BOX_SIZE, position[1] * BOX_SIZE, BOX_SIZE, BOX_SIZE)
            pygame.draw.rect(surface, color, rect)

class Food:
    def __init__(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        self.image = self.load_random_image()

    def load_random_image(self):
        assets_folder = 'assets'
        images = [f for f in os.listdir(assets_folder) if os.path.isfile(os.path.join(assets_folder, f))]
        random_image = random.choice(images)
        return pygame.image.load(os.path.join(assets_folder, random_image))

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        self.image = pygame.transform.scale(self.load_random_image(), (BOX_SIZE, BOX_SIZE))
        rect = pygame.Rect(self.position[0] * BOX_SIZE, self.position[1] * BOX_SIZE, BOX_SIZE, BOX_SIZE)
        surface.blit(self.image, rect)

def draw_background(surface): 
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = (144, 238, 144) if (x + y) % 2 == 0 else (120, 200, 120)
            rect = pygame.Rect(x * BOX_SIZE, y * BOX_SIZE, BOX_SIZE, BOX_SIZE)
            pygame.draw.rect(surface, color, rect)

def draw_text(surface, text, size, color, position):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    surface.blit(text_surface, text_rect)

async def start_screen(screen):
    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, "Press ENTER or SPACE to start", 64, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return True
        await asyncio.sleep(0)

async def lost_screen(screen, message):
    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, message, 64, (255, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        draw_text(screen, "Press ENTER or SPACE to restart", 64, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return True
        await asyncio.sleep(0)

async def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    if not await start_screen(screen):
        return

    while True:
        snake = Snake()
        food = Food()
        game_running = True

        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))

            try:
                snake.move()
            except ValueError as e:
                print(e)
                game_running = False
                if not await lost_screen(screen, str(e)):
                    return

            if snake.positions[0] == food.position:
                snake.grow_snake()
                food.randomize_position()

            draw_background(screen)
            snake.draw(screen)
            food.draw(screen)
            pygame.display.flip()
            clock.tick(10)
            await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())