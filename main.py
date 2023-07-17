import pygame
import sys
import os
import random
import inputbox
import sqlite3


def load_image(name, xy, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    image1 = pygame.transform.scale(image, xy)
    if colorkey:
        colorkey = image1.get_at((0, 0))
        image1.set_colorkey(colorkey)
    return image1


def load_level(filename):
    filename = "data/" + filename

    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def update_all():
    global level_count
    screen.fill((0, 0, 0))
    all_sprites.empty()
    grass_group.empty()
    kust_group.empty()
    coin_group.empty()
    player_group.empty()
    monster_group.empty()
    flag_group.empty()
    pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


def are_collided(left, right):
    return pygame.sprite.collide_mask(left, right) is not None


def start_screen(screen):
    result = cur.execute(f"""SELECT nick, coins FROM Results 
                             ORDER BY coins desc""").fetchone()

    intro_text = ["Добро пожаловать в игру 'Take money and escape!'",
                  "",
                  "Правила игры:",
                  "Для движения используйте клавиши WASD, для атаки - пробел",
                  "Ваша задача добраться до флага, прихватив как можно больше монет.",
                  "Кстати! За убийство монстров тоже даются монеты!",
                  "Осторожно! Не попадитесь монстру - иначе игру придется начать заново!",
                  "Для начала игры нажмите любую клавишу..."]
    if result:
        intro_text.insert(1, f"Лучший результат за все время: {result[0]}, {result[1]} монет.")

    fon = load_image('fon.jpg', (1100, 700))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 40)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                level_1()
            if event.type == pygame.QUIT:
                terminate()


def next_level_screen(screen):
    global coins
    global level_count
    intro_text = ["Поздравляем с прохождением уровня!", "",
                  f"Ваш текущий счет: {coins}",
                  "Для перехода на следующий уровень нажмите любую клавишу..."]
    screen.fill((0, 0, 0))
    fon = load_image('fon.jpg', (1100, 700))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                update_all()
                if level_count == 1:
                    level_count += 1
                    level_2()
                elif level_count == 2:
                    level_count += 1
                    level_3()
                elif level_count == 3:
                    start_screen(screen)
                return
            if event.type == pygame.QUIT:
                terminate()


def finish_screen_lose(screen):
    global coins
    global level_count
    inp = inputbox.ask(screen, 'Ваш никнейм')
    place = cur.execute(f"""SELECT COUNT(1) FROM Results WHERE coins > {coins}""").fetchone()[0]
    cur.execute(f"""INSERT INTO Results(nick, coins) 
                                         VALUES('{inp}', {coins})""")
    connection.commit()
    intro_text = ["АЙ! Вы попались монстру...", "",
                  f"Ваши монеты за игру: {coins}",
                  f"Вы на {place+1} месте среди игроков",
                  "Для прохождения игры заново нажмите любую клавишу..."]

    screen.fill((0, 0, 0))
    fon = load_image('lose.jpg', (1100, 700))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                update_all()
                level_count = 1
                coins = 0
                level_1()
                return
            if event.type == pygame.QUIT:
                terminate()


def finish_screen_win(screen):
    global coins
    global level_count
    inp = inputbox.ask(screen, 'Ваш никнейм')
    place = cur.execute(f"""SELECT COUNT(1) FROM Results WHERE coins > {coins}""").fetchone()[0]
    cur.execute(f"""INSERT INTO Results(nick, coins) 
                                     VALUES('{inp}', '{coins}')""")
    connection.commit()
    intro_text = [f"Поздравляем с прохождением игры, {inp}", "",
                  f"Ваш счет за игру: {coins}",
                  f"Вы на {place+1} месте среди игроков",
                  "Для прохождения игры заново нажмите любую клавишу..."]

    screen.fill((0, 0, 0))
    fon = load_image('winner.jpg', (1100, 700))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                update_all()
                coins = 0
                level_count = 1
                level_1()
                return
            if event.type == pygame.QUIT:
                terminate()


def generate_level(level):
    new_player, x, y = None, None, None
    x_play, y_play = 0, 0
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Grass(x, y)
            elif level[y][x] == '=':
                Grass(x, y)
                Flag(x, y)
            elif level[y][x] == '#':
                Grass(x, y)
                Kust(x, y)
            elif level[y][x] == '+':
                Grass(x, y)
                Coin(x, y)
            elif level[y][x] == '-':
                Grass(x, y)
            elif level[y][x] == '@':
                Grass(x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '-':
                Monster(x, y)
            elif level[y][x] == '@':
                x_play, y_play = x, y

    # вернем игрока, а также размер поля в клетках
    new_player = Player(x_play, y_play)
    return new_player, x, y


def level_1():
    player, level_x, level_y = generate_level(load_level('level_1.txt'))

    camera = Camera()
    running = True
    clock = pygame.time.Clock()
    while running:
        # изменяем ракурс камеры
        camera.update_camera(player)

        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in monster_group:
            sprite.walk()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                player.player_move(3)
            elif keys[pygame.K_a]:
                player.player_move(4)
            elif keys[pygame.K_w]:
                player.player_move(1)
            elif keys[pygame.K_s]:
                player.player_move(2)
            elif keys[pygame.K_SPACE]:
                player.attack()
        player.update_attack()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def level_2():
    player, level_x, level_y = generate_level(load_level('level_2.txt'))

    camera = Camera()
    running = True
    clock = pygame.time.Clock()
    while running:
        # изменяем ракурс камеры
        camera.update_camera(player)

        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in monster_group:
            sprite.walk()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                player.player_move(3)
            elif keys[pygame.K_a]:
                player.player_move(4)
            elif keys[pygame.K_w]:
                player.player_move(1)
            elif keys[pygame.K_s]:
                player.player_move(2)
            elif keys[pygame.K_SPACE]:
                player.attack()
        player.update_attack()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def level_3():
    player, level_x, level_y = generate_level(load_level('level_3.txt'))

    camera = Camera()
    running = True
    clock = pygame.time.Clock()
    while running:
        # изменяем ракурс камеры
        camera.update_camera(player)

        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        for sprite in monster_group:
            sprite.walk()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                player.player_move(3)
            elif keys[pygame.K_a]:
                player.player_move(4)
            elif keys[pygame.K_w]:
                player.player_move(1)
            elif keys[pygame.K_s]:
                player.player_move(2)
            elif keys[pygame.K_SPACE]:
                player.attack()
        player.update_attack()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheets, x, y, size, *groups):
        super().__init__(*groups)
        self.frames = {}
        for action, anim in sheets.items():
            animation, columns, rows = anim[0], anim[1], anim[2]
            self.cut_sheet(animation, columns, rows, size, action)
        self.timer_to_action = [-1, '']
        self.quit = -1
        self.dead = -1
        self.cur_frame = {}
        self.action = 'walk'
        self.cur_frame['walk'] = 0
        self.cur_frame['attack'] = 0
        self.cur_frame['dead'] = 0
        self.image = self.frames['walk'][self.cur_frame['walk']]
        self.rect = self.image.get_rect().move(
            tile_width * x, tile_height * y)

    def cut_sheet(self, sheet, columns, rows, size, action):
        self.rect1 = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        self.frames[action] = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (i * sheet.get_width() // columns, 0)
                new_frame = sheet.subsurface(pygame.Rect(
                    frame_location, self.rect1.size))
                new_frame = pygame.transform.scale(new_frame, (size, size))
                self.frames[action].append(new_frame)

    def update(self):
        self.cur_frame[self.action] = (self.cur_frame[self.action] + 1) % len(self.frames[self.action])
        self.image = self.frames[self.action][self.cur_frame[self.action]]
        if self.quit != -1:
            if self.quit == 0:
                finish_screen_lose(screen)
            else:
                self.quit = self.quit - 1
        if self.dead != -1:
            self.dead = self.dead - 1
        if self.dead == 0:
            self.kill()
        if self.timer_to_action[0] == 0:
            self.action = self.timer_to_action[1]
            self.timer_to_action = [-1, '']
            self.update()
        elif self.timer_to_action[0] != -1:
            self.timer_to_action[0] = self.timer_to_action[0] - 1


class Flag(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(flag_group, all_sprites)
        self.image = tile_images['flag']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(coin_group, all_sprites)
        self.image = tile_images['coin']
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Kust(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(kust_group, all_sprites)
        self.image = tile_images['kust']
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Grass(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(grass_group, all_sprites)
        self.image = tile_images['grass']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update_camera(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Player(AnimatedSprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_animations, pos_x, pos_y, 80, player_group, all_sprites)
        self.mask = pygame.mask.from_surface(self.image)
        self.vx = self.vy = 4

    def get_coin(self, coin):
        global coins
        coins += 5
        coin.kill()

    def player_move(self, direction):
        x, y = self.rect.x, self.rect.y
        self.update()
        if direction == 3:
            self.rect = self.rect.move(self.vx, 0)
        elif direction == 4:
            self.rect = self.rect.move(-self.vx, 0)
        elif direction == 1:
            self.rect = self.rect.move(0, -self.vy)
        elif direction == 2:
            self.rect = self.rect.move(0, self.vy)
        if pygame.sprite.spritecollideany(self, kust_group, are_collided):
            self.rect.x = x
            self.rect.y = y
        coin = pygame.sprite.spritecollideany(self, coin_group, are_collided)
        if coin:
            coin_music.play()
            self.get_coin(coin)
        if pygame.sprite.spritecollideany(self, flag_group, are_collided):
            flag_music.play()
            if level_count == 3:
                finish_screen_win(screen)
            else:
                next_level_screen(screen)

    def attack(self):
        global coins
        if self.timer_to_action[0] == -1:
            self.timer_to_action = [18, 'walk']
        self.action = 'attack'
        near_monster = pygame.sprite.spritecollideany(self, monster_group, pygame.sprite.collide_circle_ratio(1.05))
        if near_monster and near_monster.dead == -1:
            near_monster.dead = 15
            coins += 10
            near_monster.action = 'dead'

    def update_attack(self):
        if self.action == 'attack':
            self.update()


class Monster(AnimatedSprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(monster_animations, pos_x, pos_y, 90, monster_group, all_sprites)
        self.mask = pygame.mask.from_surface(self.image)
        self.dead = -1
        self.vx = self.vy = 3
        self.direction = random.randint(1, 4)

    def walk(self):
        x, y = self.rect.x, self.rect.y
        self.update()
        if self.direction == 3:
            self.rect = self.rect.move(self.vx, 0)
        elif self.direction == 4:
            self.rect = self.rect.move(-self.vx, 0)
        elif self.direction == 1:
            self.rect = self.rect.move(0, -self.vy)
        elif self.direction == 2:
            self.rect = self.rect.move(0, self.vy)
        if pygame.sprite.spritecollideany(self, kust_group):
            self.rect.x = x
            self.rect.y = y
            self.direction = random.randint(1, 4)
        if pygame.sprite.spritecollideany(self, flag_group):
            self.rect.x = x
            self.rect.y = y
            self.direction = random.randint(1, 4)
        if pygame.sprite.spritecollideany(self, player_group, are_collided):
            self.rect.x = x
            self.rect.y = y
            if self.dead == -1:
                self.action = 'attack'
                if self.quit == -1:
                    self.quit = 18
                monster_music.play()
            self.direction = random.randint(1, 4)


# основной персонаж
player = None
FPS = 30

# группы спрайтов
all_sprites = pygame.sprite.Group()
grass_group = pygame.sprite.Group()
kust_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
flag_group = pygame.sprite.Group()

# текущий уровень и количество очков
level_count = 1
coins = 0
connection = sqlite3.connect("Game.db")
cur = connection.cursor()


if __name__ == '__main__':
    pygame.init()
    pygame.mixer.pre_init()
    coin_music = pygame.mixer.Sound("sounds/take.wav")
    flag_music = pygame.mixer.Sound("sounds/flag.wav")
    monster_music = pygame.mixer.Sound("sounds/monster.wav")
    pygame.mixer.music.load("sounds/fon.wav")
    pygame.mixer.music.play(-1, 0.0, 2000)
    pygame.display.set_caption('Take money and escape!')
    size = width, height = 1100, 700
    screen = pygame.display.set_mode(size)

    tile_images = {
        'kust': load_image('kust.png', (70, 100), 1),
        'grass': load_image('grass.png', (100, 100)),
        'coin': load_image('coin.png', (50, 50), 1),
        'flag': load_image('flag1.png', (80, 80), 1)
    }
    player_walk = load_image('ggg.png', (640, 80), 1)
    player_attack = load_image('player_attack.png', (160, 80), 1)
    player_animations = {'walk': [player_walk, 8, 1], 'attack': [player_attack, 2, 1]}
    monster_walk = load_image('skelet_walk.png', (1040, 80), 1)
    monster_dead = load_image('skeleton_dead.png', (1200, 80), 1)
    monster_attack = load_image('skeleton_attack.png', (1440, 80), 1)
    monster_animations = {'walk': [monster_walk, 13, 1], 'dead': [monster_dead, 15, 1], 'attack': [monster_attack, 18, 1]}

    tile_width = tile_height = 100
    start_screen(screen)
    pygame.display.flip()
    terminate()
