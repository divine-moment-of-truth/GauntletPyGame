import pygame as pg
from random import uniform
from settings import *
from tilemap import collide_hit_rect
vec = pg.math.Vector2

def collide_with_walls(sprite, group, direction):
        if direction == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                # if the players center is greater than the wall center then the player is on the right hand side of the wall
                if hits[0].rect.centerx > sprite.hit_rect.rect.centerx:
                    # puts the player sprite to the left hand side of the wall sprite (players top left hand corner) position minus the players width
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                 # if the players center is less than the wall center then the player is on the left hand side of the wall
                if hits[0].rect.centerx < sprite.hit_rect.rect.centerx:
                    # puts the player sprite to the right hand side of the wall
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        if direction == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                # if the players center is greater than the wall center then the player must be underneath the wall
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    # puts the player sprite at the top of the wall sprite - minus the player sprites height
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                # if the players center is less than the wall center then the player must be above the wall
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        # self.vx, self.vy = 0, 0
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        # self.x = x * TILESIZE
        # self.y = y * TILESIZE
        self.pos = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH

    def get_keys(self):
        self.rot_speed = 0
        # self.vx, self.vy = 0, 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
            # UP key causes the player to move forward in the angle they are facing
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            # when moving backwards player moves at half the speed (divide by 2)
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, self.pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)

            # below line is for diagonal movements
        # if self.vel.x != 0 and self.vel.y != 0:
        #    self.vel *= 0.7071

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        # self.x += self.vx * self.game.dt
        # self.y += self.vy * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.wall_img
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = MOB_IMG
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y) * TILESIZE
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
        self.acc += self.vel * -1
        self.vel += self.acc * self.acc.game.dt
        # ** 2 means the square root
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()

        def draw_health(self):
            if self.health > 60:
                col = GREEN
            elif self.health > 30:
                col = YELLOW
            else:
                col = RED
            width = int(self.rect.width * self.health / MOB_HEALTH)
            self.health_bar = pg.Rect(0, 0, width, 7)
            if self.health < MOB_HEALTH:
                pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        # below line makes a copy of the pos
        self.pos = vec(pos)
        self.pos = pos
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = di.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME
            self.kill()