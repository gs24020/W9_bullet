import pygame
import random
import sys
from abc import ABC, abstractmethod

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont("malgungothic", 22)
big_font = pygame.font.SysFont("malgungothic", 60)

WHITE = (245,245,245)
BLACK = (30,30,30)
BLUE = (70,130,255)
RED = (220,80,80)
GREEN = (80,200,120)
PURPLE = (150,0,200)
YELLOW = (255,220,0)

class GameObject(ABC):
    def __init__(self):
        self._alive = True

    @property
    def is_alive(self):
        return self._alive

    def destroy(self):
        self._alive = False

    @property
    def can_collide_with_player(self):
        return False

    @property
    def can_collide_with_bullet(self):
        return False

    @property
    def is_bullet(self):
        return False

    @property
    @abstractmethod
    def rect(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

    def on_player_collision(self, player):
        pass

    def on_bullet_collision(self, bullet, player):
        pass

class Player(GameObject):
    def __init__(self):
        super().__init__()
        self._x = 100
        self._y = 300
        self._size = 40
        self._speed = 5
        self._max_hp = 100
        self._hp = 100
        self._bomb = 3

    @property
    def hp(self):
        return self._hp

    @property
    def max_hp(self):
        return self._max_hp

    @property
    def bomb(self):
        return self._bomb

    @property
    def rect(self):
        return pygame.Rect(self._x, self._y, self._size, self._size)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self._y -= self._speed
        if keys[pygame.K_s]: self._y += self._speed
        if keys[pygame.K_a]: self._x -= self._speed
        if keys[pygame.K_d]: self._x += self._speed

        self._x = max(0, min(WIDTH - self._size, self._x))
        self._y = max(0, min(HEIGHT - self._size, self._y))

    def shoot(self):
        return Bullet(self._x + self._size, self._y + self._size//2)

    def use_bomb(self):
        if self._bomb > 0:
            self._bomb -= 1
            return True
        return False

    def take_damage(self, dmg):
        self._hp -= dmg
        if self._hp <= 0:
            self.destroy()

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

class Bullet(GameObject):
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y
        self._speed = 10
        self._r = 5
        self._damage = 3

    @property
    def is_bullet(self):
        return True

    @property
    def damage(self):
        return self._damage

    @property
    def rect(self):
        return pygame.Rect(self._x, self._y, self._r*2, self._r*2)

    def update(self):
        self._x += self._speed
        if self._x > WIDTH:
            self.destroy()

    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (int(self._x), int(self._y)), self._r)

class EnemyBullet(GameObject):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self._x = x
        self._y = y
        self._vx = vx
        self._vy = vy
        self._r = 6
        self._damage = 10

    @property
    def can_collide_with_player(self):
        return True

    @property
    def rect(self):
        return pygame.Rect(self._x, self._y, self._r*2, self._r*2)

    def update(self):
        self._x += self._vx
        self._y += self._vy
        if self._x<0 or self._x>WIDTH or self._y<0 or self._y>HEIGHT:
            self.destroy()

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self._x), int(self._y)), self._r)

    def on_player_collision(self, player):
        player.take_damage(self._damage)
        self.destroy()

class Boss(GameObject):
    def __init__(self):
        super().__init__()
        self._x = WIDTH - 200
        self._y = HEIGHT//2
        self._size = 120
        self._max_hp = 400
        self._hp = 400
        self._phase = 1
        self._timer = 0
        self._vx = -2
        self._vy = 2
        self._damage = 10

    @property
    def hp(self):
        return self._hp

    @property
    def max_hp(self):
        return self._max_hp

    @property
    def phase(self):
        return self._phase

    @property
    def can_collide_with_player(self):
        return True

    @property
    def can_collide_with_bullet(self):
        return True

    @property
    def rect(self):
        return pygame.Rect(self._x, self._y, self._size, self._size)

    def teleport(self):
        self._x = random.randint(WIDTH//2, WIDTH - self._size)
        self._y = random.randint(0, HEIGHT - self._size)

    def update(self):
        self._timer += 1

        self._x += self._vx
        self._y += self._vy

        if self._y < 0 or self._y > HEIGHT - self._size:
            self._vy *= -1
        if self._x < WIDTH//2 or self._x > WIDTH - self._size:
            self._vx *= -1

        if self._phase >= 3 and self._timer % 120 == 0:
            self.teleport()

        if self._phase == 1:
            if self._timer % 60 == 0:
                objects.append(EnemyBullet(self._x, self._y+60, -6, 0))

        elif self._phase == 2:
            if self._timer % 40 == 0:
                for i in range(-8,9,2):
                    objects.append(EnemyBullet(self._x, self._y+60, -5, i))

        elif self._phase == 3:
            if self._timer % 25 == 0:
                for i in range(12):
                    angle = i * 30
                    vec = pygame.math.Vector2(1,0).rotate(angle)
                    objects.append(EnemyBullet(self._x+60, self._y+60, vec.x*4, vec.y*4))

        elif self._phase == 4:
            if self._timer % 15 == 0:
                px, py = player.rect.center
                dx = px - self._x
                dy = py - self._y
                dist = max(1,(dx**2+dy**2)**0.5)
                objects.append(EnemyBullet(self._x+60, self._y+60, dx/dist*6, dy/dist*6))

    def draw(self, surface):
        color = RED if self._phase == 1 else PURPLE if self._phase == 2 else GREEN if self._phase == 3 else BLACK
        pygame.draw.rect(surface, color, self.rect)

        bar_width = 100
        bar_height = 10

        center_x = self._x + self._size // 2
        bar_x = center_x - bar_width // 2
        bar_y = self._y + self._size // 2 - 30

        ratio = self._hp / self._max_hp
        hp_width = int(bar_width * ratio)

        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        pygame.draw.rect(surface, RED, (bar_x, bar_y, hp_width, bar_height))

        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

        hp_text = font.render(f"{self._hp}", True, BLACK)
        surface.blit(
            hp_text,
            (center_x - hp_text.get_width() // 2, bar_y - 20)
        )

    def take_damage(self, dmg):
        if not self.is_alive:
            return

        self._hp -= dmg

        if self._hp < 300: self._phase = 2
        if self._hp < 200: self._phase = 3
        if self._hp < 100: self._phase = 4

        if self._hp <= 0:
            self._hp = 0
            self.destroy()

    def on_player_collision(self, player):
        player.take_damage(self._damage)

    def on_bullet_collision(self, bullet, player):
        if bullet.is_alive:
            self.take_damage(bullet.damage)
            bullet.destroy()

def draw_ui(surface, player, boss):
    # ===== 플레이어 UI =====
    bar_x, bar_y = 20, 20
    bar_w, bar_h = 200, 20

    pygame.draw.rect(surface, (100,100,100), (bar_x, bar_y, bar_w, bar_h))

    ratio = player.hp / player.max_hp
    current_w = int(bar_w * ratio)
    pygame.draw.rect(surface, GREEN, (bar_x, bar_y, current_w, bar_h))

    pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_w, bar_h), 2)

    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, BLACK)
    surface.blit(hp_text, (20, 45))

    surface.blit(font.render(f"Bomb: {player.bomb}", True, BLACK), (20, 80))
    surface.blit(font.render("SPACE 발사 / E 폭탄", True, BLACK), (20, 110))

    # ===== 보스 UI (우상단) =====
    boss_bar_w = 250
    boss_bar_h = 25

    boss_bar_x = WIDTH - boss_bar_w - 30
    boss_bar_y = 20

    # 배경
    pygame.draw.rect(
        surface,
        (80,80,80),
        (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h)
    )

    # 현재 HP
    boss_ratio = boss.hp / boss.max_hp
    boss_current_w = int(boss_bar_w * boss_ratio)

    pygame.draw.rect(
        surface,
        RED,
        (boss_bar_x, boss_bar_y, boss_current_w, boss_bar_h)
    )

    # 테두리
    pygame.draw.rect(
        surface,
        BLACK,
        (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h),
        2
    )

    # HP 텍스트
    boss_hp_text = font.render(
        f"BOSS HP : {boss.hp}/{boss.max_hp}",
        True,
        BLACK
    )

    surface.blit(
        boss_hp_text,
        (boss_bar_x + 10, boss_bar_y + 30)
    )

    # 상태(Phase) 표시
    phase_names = {
        1: "NORMAL",
        2: "SPREAD",
        3: "CIRCLE",
        4: "BERSERK"
    }

    state_text = font.render(
        f"STATE : {phase_names[boss.phase]}",
        True,
        BLACK
    )

    surface.blit(
        state_text,
        (boss_bar_x + 10, boss_bar_y + 60)
    )

player = Player()
boss = Boss()
objects = [player, boss]

game_win = False
game_over = False

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player.is_alive and not game_win:
                objects.append(player.shoot())
            if event.key == pygame.K_e:
                if player.use_bomb():
                    for obj in objects:
                        if isinstance(obj, EnemyBullet):
                            obj.destroy()
                    boss.take_damage(30)

    if not game_over and not game_win:
        for obj in objects:
            obj.update()

        bullets = [o for o in objects if o.is_bullet]
        targets = [o for o in objects if o.can_collide_with_bullet]
        player_targets = [o for o in objects if o.can_collide_with_player]

        for obj in player_targets:
            if obj.is_alive and player.rect.colliderect(obj.rect):
                obj.on_player_collision(player)

        for b in bullets:
            for t in targets:
                if b.is_alive and t.is_alive and b.rect.colliderect(t.rect):
                    t.on_bullet_collision(b, player)

        objects = [o for o in objects if o.is_alive]

        if not boss.is_alive:
            game_win = True

        if not player.is_alive:
            game_over = True

    screen.fill(WHITE)

    for obj in objects:
        obj.draw(screen)

    draw_ui(screen, player, boss)

    if game_win:
        txt = big_font.render("GAME WIN!", True, GREEN)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 70))
        if player.hp == player.max_hp:
            perfect_txt = font.render("PERFECT", True, BLUE)
            screen.blit(perfect_txt, (WIDTH // 2 - perfect_txt.get_width() // 2, HEIGHT // 2))

    if game_over:
        txt = big_font.render("GAME OVER", True, RED)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))


    pygame.display.flip()
