import asyncio
import pygame
import random
from abc import ABC, abstractmethod

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss Shooter")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 72)

WHITE = (245, 245, 245)
BLACK = (30, 30, 30)
BLUE = (70, 130, 255)
RED = (220, 80, 80)
GREEN = (80, 200, 120)
PURPLE = (150, 0, 200)

objects = []
player = None
boss = None
game_win = False
game_over = False


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

        if keys[pygame.K_w]:
            self._y -= self._speed

        if keys[pygame.K_s]:
            self._y += self._speed

        if keys[pygame.K_a]:
            self._x -= self._speed

        if keys[pygame.K_d]:
            self._x += self._speed

        self._x = max(0, min(WIDTH - self._size, self._x))
        self._y = max(0, min(HEIGHT - self._size, self._y))

    def shoot(self):
        return Bullet(
            self._x + self._size,
            self._y + self._size // 2
        )

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
        return pygame.Rect(
            self._x,
            self._y,
            self._r * 2,
            self._r * 2
        )

    def update(self):

        self._x += self._speed

        if self._x > WIDTH:
            self.destroy()

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            BLACK,
            (int(self._x), int(self._y)),
            self._r
        )


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
        return pygame.Rect(
            self._x,
            self._y,
            self._r * 2,
            self._r * 2
        )

    def update(self):

        self._x += self._vx
        self._y += self._vy

        if (
            self._x < 0
            or self._x > WIDTH
            or self._y < 0
            or self._y > HEIGHT
        ):
            self.destroy()

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            RED,
            (int(self._x), int(self._y)),
            self._r
        )

    def on_player_collision(self, player):

        player.take_damage(self._damage)
        self.destroy()


class Boss(GameObject):

    def __init__(self):
        super().__init__()

        self._x = WIDTH - 200
        self._y = HEIGHT // 2

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
        return pygame.Rect(
            self._x,
            self._y,
            self._size,
            self._size
        )

    def teleport(self):

        self._x = random.randint(
            WIDTH // 2,
            WIDTH - self._size
        )

        self._y = random.randint(
            0,
            HEIGHT - self._size
        )

    def update(self):

        global objects

        self._timer += 1

        self._x += self._vx
        self._y += self._vy

        if self._y < 0 or self._y > HEIGHT - self._size:
            self._vy *= -1

        if self._x < WIDTH // 2 or self._x > WIDTH - self._size:
            self._vx *= -1

        if self._phase >= 3 and self._timer % 120 == 0:
            self.teleport()

        if self._phase == 1:

            if self._timer % 60 == 0:

                objects.append(
                    EnemyBullet(
                        self._x,
                        self._y + 60,
                        -6,
                        0
                    )
                )

        elif self._phase == 2:

            if self._timer % 40 == 0:

                for i in range(-8, 9, 2):

                    objects.append(
                        EnemyBullet(
                            self._x,
                            self._y + 60,
                            -5,
                            i
                        )
                    )

        elif self._phase == 3:

            if self._timer % 25 == 0:

                for i in range(12):

                    angle = i * 30

                    vec = pygame.math.Vector2(
                        1,
                        0
                    ).rotate(angle)

                    objects.append(
                        EnemyBullet(
                            self._x + 60,
                            self._y + 60,
                            vec.x * 4,
                            vec.y * 4
                        )
                    )

        elif self._phase == 4:

            if self._timer % 15 == 0:

                px, py = player.rect.center

                dx = px - self._x
                dy = py - self._y

                dist = max(
                    1,
                    (dx ** 2 + dy ** 2) ** 0.5
                )

                objects.append(
                    EnemyBullet(
                        self._x + 60,
                        self._y + 60,
                        dx / dist * 6,
                        dy / dist * 6
                    )
                )

    def draw(self, surface):

        color = (
            RED if self._phase == 1
            else PURPLE if self._phase == 2
            else GREEN if self._phase == 3
            else BLACK
        )

        pygame.draw.rect(surface, color, self.rect)

    def take_damage(self, dmg):

        if not self.is_alive:
            return

        self._hp -= dmg

        if self._hp < 300:
            self._phase = 2

        if self._hp < 200:
            self._phase = 3

        if self._hp < 100:
            self._phase = 4

        if self._hp <= 0:
            self.destroy()

    def on_player_collision(self, player):
        player.take_damage(self._damage)

    def on_bullet_collision(self, bullet, player):

        if bullet.is_alive:

            self.take_damage(bullet.damage)
            bullet.destroy()


def draw_ui(surface, player, boss):

    pygame.draw.rect(
        surface,
        (100, 100, 100),
        (20, 20, 200, 20)
    )

    ratio = player.hp / player.max_hp

    pygame.draw.rect(
        surface,
        GREEN,
        (20, 20, int(200 * ratio), 20)
    )

    hp_text = font.render(
        f"HP: {player.hp}/{player.max_hp}",
        True,
        BLACK
    )

    surface.blit(hp_text, (20, 50))

    bomb_text = font.render(
        f"Bomb: {player.bomb}",
        True,
        BLACK
    )

    surface.blit(bomb_text, (20, 80))

    guide_text = font.render(
        "SPACE Shoot / E Bomb",
        True,
        BLACK
    )

    surface.blit(guide_text, (20, 110))

    boss_text = font.render(
        f"Boss HP: {boss.hp}",
        True,
        BLACK
    )

    surface.blit(boss_text, (WIDTH - 250, 20))


player = Player()
boss = Boss()

objects = [player, boss]


async def main():

    global objects
    global game_win
    global game_over

    while True:

        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if (
                    event.key == pygame.K_SPACE
                    and player.is_alive
                    and not game_win
                ):
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

            bullets = [
                o for o in objects
                if o.is_bullet
            ]

            targets = [
                o for o in objects
                if o.can_collide_with_bullet
            ]

            player_targets = [
                o for o in objects
                if o.can_collide_with_player
            ]

            for obj in player_targets:

                if (
                    obj.is_alive
                    and player.rect.colliderect(obj.rect)
                ):
                    obj.on_player_collision(player)

            for b in bullets:

                for t in targets:

                    if (
                        b.is_alive
                        and t.is_alive
                        and b.rect.colliderect(t.rect)
                    ):
                        t.on_bullet_collision(b, player)

            objects = [
                o for o in objects
                if o.is_alive
            ]

            if not boss.is_alive:
                game_win = True

            if not player.is_alive:
                game_over = True

        screen.fill(WHITE)

        for obj in objects:
            obj.draw(screen)

        draw_ui(screen, player, boss)

        if game_win:

            txt = big_font.render(
                "GAME WIN!",
                True,
                GREEN
            )

            screen.blit(
                txt,
                (WIDTH // 2 - 180, HEIGHT // 2 - 50)
            )

        if game_over:

            txt = big_font.render(
                "GAME OVER",
                True,
                RED
            )

            screen.blit(
                txt,
                (WIDTH // 2 - 220, HEIGHT // 2 - 50)
            )

        pygame.display.flip()

        await asyncio.sleep(0)


asyncio.run(main())