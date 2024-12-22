from pygame import *
from random import randint
from time import time as timer


class GameSprite(sprite.Sprite):
    '''класс родитель для спрайтов'''

    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        '''конструктор класса'''
        super().__init__()
        # каждый спрайт хранит изображение image
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        # каждый спрайт - это прямоугольник
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        '''отобразить персонажа'''
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    '''клас наследник для спрайта игроки(управляется стрелками)'''

    def update(self):
        '''перемещение игрока клавишами'''
        keys_pressed = key.get_pressed()
        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        '''стрельба'''
        bullet = Bullet('bullet.png', self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)

class Enemy(GameSprite):
    '''клас наследник для спрайта врага(управляется стрелками)'''

    def update(self):
        '''перемещение автоматическое - координата у постоянно растет'''
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            # если противник выходит за поле
            self.rect.x = randint(80, win_width-80)
            self.rect.y = 0
            lost += 1

class Asteroid(GameSprite):
    '''клас наследник для спрайта астеройда(управляется стрелками)'''

    def update(self):
        '''перемещение автоматическое - координата у постоянно растет'''
        self.rect.y += self.speed
        if self.rect.y > win_height:
            # если противник выходит за поле
            self.rect.x = randint(80, win_width-80)
            self.rect.y = 0

class Bullet(GameSprite):
    '''класс спрайта пули'''
    def update(self):
        '''перемещается автоматически снизу вверх(координата Y)'''
        self.rect.y -= self.speed
        # пуля изчезнет, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()

class Life(sprite.Sprite):
    '''класс для жизней'''
    def reset(self):
        '''отобразить персонажа'''
        window.blit(self.image, (self.rect.x, self.rect.y))

# создаем окно игры
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption('Зомби против растений')
background = transform.scale(image.load('ground.png'), (win_width, win_height))

#фоновая музыка
mixer.init()
mixer.music.load('PVZ_-_Main_Menu_76859213.mp3')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')  # звук выстрела

# шрифты
font.init()
font1 = font.SysFont('Times New Roman', 80)
font2 = font.SysFont('Times New Roman', 36)

score = 0 # сбито
lost = 0 # пропущено
maxlost = 10
goal = 30 # цель
life = 3 # жизни

win = font1.render('ПОБЕДА', True, 'cornsilk1')
lose = font1.render('ПОРАЖЕНИЕ', True, 'crimson')
restert = font1.render('ПЕРЕЗАПУСК', True, 'cornsilk1')

# спрайты игры
ship = Player('plant1.png', 5, win_height-90, 80, 60, 10)

bullets = sprite.Group()
monsters = sprite.Group()
for i in range(5):
    # создание нескольких противников
    monster = Enemy('zombie.png', randint(80, win_width-80), -40, 100,80, randint(1, 3))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(2):
    # создание нескольких астероидов
    asteroid = Asteroid('asteroid.png', randint(30, win_width-30), -40, 80,50, randint(1, 5))
    asteroids.add(asteroid)


# переменные для игрового цикла
game = True
finish = False
rel_time = False
num_fire = 0

# игровой цикл
while game:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and not rel_time:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True

    if not finish:
        window.blit(background, (0, 0))
        ship.reset()
        ship.update()
        monsters.update()
        bullets.update()
        bullets.draw(window)
        asteroids.draw(window)
        asteroids.update()
        # ПЕРЕЗАРЯДКА

        if rel_time:
            now_time = timer()
            if now_time - last_time < 3 :
                rel_text = font2.render('ПЕРЕЗАРЯДКА', 1, 'aquamarine')
                window.blit(rel_text, (250, 400))
            else:
                num_fire = 0
                rel_time = False

        if life == 3:
            life_color = 'darkolivegreen1'
        if life == 2:
            life_color = 'darkgoldenrod1'
        if life == 1:
            life_color = 'red'
        if life == 0:
            life_color = 'darkred'
        life_score = font1.render(str(life), 1, life_color)
        window.blit(life_score,(600, 20))

        # проверка столкновения пуль и монстров( и то и другое изчезают)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        # collides - словарь хранящий столкновения пуль и монстров
        for c in collides:
            # увеличиваем счетчик врагов на 1
            score += 1
            # новый противник
            monster = Enemy('zombie.png', randint(80, win_width - 80), -40, 100, 80, randint(1, 3))
            monsters.add(monster)

        # Если спрай коснулся врага или астеройда, уменьшаем жизнь
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1

        # ПОРАЖЕНИЕ - пропустили много противников или столкнулись с одним из них
        if lost >= maxlost or life == 0:
            finish = True
            window.blit(lose, (200, 200))

        # ПОБЕДА - сбито достаточно кораблей
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        # создаем счетчики сбитых и не сбитых противников, отображаем их
        text = font2.render(f'Счёт: {str(score)}', 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render(f'Пропущено: {str(lost)}', 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        monsters.update()
        monsters.draw(window)

        display.update()
    else:
        time.delay(3000)
        finish = False
        score = 0
        lost = 0
        for b in bullets:
            b.kill()

        for m in monsters:
            m.kill()

        for i in range(5):
            # создание нескольких противников
            monster = Enemy('zombie.png', randint(80, win_width - 80), -40, 100, 80, randint(1, 3))
            monsters.add(monster)



    time.delay(50)