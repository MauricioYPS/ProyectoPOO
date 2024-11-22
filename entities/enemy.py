# entities/enemy.py

import pygame
from entities.entity import Entity
import random
import math

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.speed = 2
        self.health = 100
        self.direction = pygame.math.Vector2(0, 0)
        self.state = 'idle'  # Estados posibles: 'idle', 'patrolling', 'wandering', 'chasing', 'attacking', 'charging'
        self.detection_radius = 150
        self.attack_cooldown = 0  # Tiempo entre ataques en frames
        self.target_player_id = None  # ID del jugador objetivo
        self.target_player_pos = None  # Posición del jugador objetivo

    def update(self, player_positions, send_damage_callback, walls=None):
        if self.health <= 0:
            return

        # Decrementar el cooldown de ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Llamar al método específico de la subclase
        self.behavior(player_positions, send_damage_callback, walls)

    def behavior(self, player_positions, send_damage_callback, walls):
        pass  # Será implementado en las subclases

    def attack(self, player_id, send_damage_callback):
        if self.attack_cooldown <= 0:
            damage = 10
            send_damage_callback(player_id, damage)
            self.attack_cooldown = 60  # 1 segundo de cooldown si el juego va a 60 FPS

    def detect_player(self, player_positions):
        closest_player_id = None
        closest_player_pos = None
        min_distance = self.detection_radius

        for player_id, pos in player_positions.items():
            dx = pos['x'] - self.rect.centerx
            dy = pos['y'] - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance < min_distance:
                min_distance = distance
                closest_player_id = player_id
                closest_player_pos = pos

        return closest_player_id, closest_player_pos, min_distance

    def move(self, dx, dy, walls=None):
        # Mover en X
        self.rect.x += dx
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dx > 0:
                        self.rect.right = wall.left
                    elif dx < 0:
                        self.rect.left = wall.right
                    break

        # Mover en Y
        self.rect.y += dy
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dy > 0:
                        self.rect.bottom = wall.top
                    elif dy < 0:
                        self.rect.top = wall.bottom
                    break

class PatrollingEnemy(Enemy):
    def __init__(self, x, y, patrol_points):
        super().__init__(x, y)
        self.patrol_points = patrol_points
        self.current_patrol_point = 0
        self.state = 'patrolling'

    def behavior(self, player_positions, send_damage_callback, walls=None):
        if self.state == 'patrolling':
            self.patrol(walls)
            player_id, player_pos, _ = self.detect_player(player_positions)
            if player_id is not None:
                self.state = 'chasing'
                self.target_player_id = player_id
                self.target_player_pos = player_pos
        elif self.state == 'chasing':
            player_id, player_pos, _ = self.detect_player(player_positions)
            if player_id is None:
                self.state = 'patrolling'
                self.target_player_id = None
                self.target_player_pos = None
            else:
                self.target_player_id = player_id
                self.target_player_pos = player_pos
                self.chase(self.target_player_pos, walls)
                if self.rect.colliderect(pygame.Rect(self.target_player_pos['x'], self.target_player_pos['y'], 40, 40)):
                    self.state = 'attacking'
        elif self.state == 'attacking':
            player_pos = player_positions.get(self.target_player_id)
            if player_pos and self.rect.colliderect(pygame.Rect(player_pos['x'], player_pos['y'], 40, 40)):
                self.attack(self.target_player_id, send_damage_callback)
            else:
                self.state = 'chasing'
                self.target_player_pos = player_positions.get(self.target_player_id)

    def patrol(self, walls=None):
        if not self.patrol_points:
            return

        target_point = self.patrol_points[self.current_patrol_point]
        dx = target_point[0] - self.rect.x
        dy = target_point[1] - self.rect.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
        else:
            if distance != 0:
                self.direction.x = dx / distance
                self.direction.y = dy / distance
                self.move(self.direction.x * self.speed, self.direction.y * self.speed, walls)

    def chase(self, target_player_pos, walls=None):
        dx = target_player_pos['x'] - self.rect.x
        dy = target_player_pos['y'] - self.rect.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.direction.x = dx / distance
            self.direction.y = dy / distance
            self.move(self.direction.x * self.speed, self.direction.y * self.speed, walls)

# Aplica cambios similares en las otras clases de enemigos

class RandomEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.state = 'wandering'
        self.wander_time = random.randint(60, 180)
        self.direction = pygame.math.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        if self.direction.length() == 0:
            self.direction = pygame.math.Vector2(1, 0)

    def behavior(self, player_positions, send_damage_callback, walls=None):
        if self.state == 'wandering':
            self.wander(walls)
            player_id, player_pos, _ = self.detect_player(player_positions)
            if player_id is not None:
                self.state = 'chasing'
                self.target_player_id = player_id
                self.target_player_pos = player_pos
        elif self.state == 'chasing':
            player_id, player_pos, _ = self.detect_player(player_positions)
            if player_id is None:
                self.state = 'wandering'
                self.target_player_id = None
                self.target_player_pos = None
            else:
                self.target_player_id = player_id
                self.target_player_pos = player_pos
                self.chase(self.target_player_pos, walls)
                if self.rect.colliderect(pygame.Rect(self.target_player_pos['x'], self.target_player_pos['y'], 40, 40)):
                    self.state = 'attacking'
        elif self.state == 'attacking':
            player_pos = player_positions.get(self.target_player_id)
            if player_pos and self.rect.colliderect(pygame.Rect(player_pos['x'], player_pos['y'], 40, 40)):
                self.attack(self.target_player_id, send_damage_callback)
            else:
                self.state = 'chasing'
                self.target_player_pos = player_positions.get(self.target_player_id)

    def wander(self, walls=None):
        self.move(self.direction.x * self.speed, self.direction.y * self.speed, walls)
        self.wander_time -= 1
        if self.wander_time <= 0:
            self.wander_time = random.randint(60, 180)
            self.direction = pygame.math.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
            if self.direction.length() == 0:
                self.direction = pygame.math.Vector2(1, 0)

    def chase(self, target_player_pos, walls=None):
        dx = target_player_pos['x'] - self.rect.x
        dy = target_player_pos['y'] - self.rect.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.direction.x = dx / distance
            self.direction.y = dy / distance
            self.move(self.direction.x * self.speed, self.direction.y * self.speed, walls)

class AggressiveEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 200
        self.speed = 1
        self.state = 'idle'

    def behavior(self, player_positions, send_damage_callback, walls=None):
        if self.state == 'idle':
            player_id, player_pos, _ = self.detect_player(player_positions)
            if player_id is not None:
                self.state = 'chasing'
                self.target_player_id = player_id
                self.target_player_pos = player_pos
        elif self.state == 'chasing':
            player_id, player_pos, _ = self.detect_player(player_positions)
            if player_id is None:
                self.state = 'idle'
                self.target_player_id = None
                self.target_player_pos = None
            else:
                self.target_player_id = player_id
                self.target_player_pos = player_pos
                self.chase(self.target_player_pos, walls)
                if self.rect.colliderect(pygame.Rect(self.target_player_pos['x'], self.target_player_pos['y'], 40, 40)):
                    self.state = 'attacking'
        elif self.state == 'attacking':
            player_pos = player_positions.get(self.target_player_id)
            if player_pos and self.rect.colliderect(pygame.Rect(player_pos['x'], player_pos['y'], 40, 40)):
                self.attack(self.target_player_id, send_damage_callback)
            else:
                self.state = 'chasing'
                self.target_player_pos = player_positions.get(self.target_player_id)

    def chase(self, target_player_pos, walls=None):
        dx = target_player_pos['x'] - self.rect.x
        dy = target_player_pos['y'] - self.rect.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.direction.x = dx / distance
            self.direction.y = dy / distance
            self.move(self.direction.x * self.speed, self.direction.y * self.speed, walls)

class StationaryEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.state = 'idle'
        self.charge_speed = 5

    def behavior(self, player_positions, send_damage_callback, walls=None):
        if self.state == 'idle':
            player_id, player_pos, distance = self.detect_player(player_positions)
            if player_id and distance < self.detection_radius / 2:
                self.state = 'charging'
                self.target_player_id = player_id
                self.target_player_pos = player_pos
                dx = self.target_player_pos['x'] - self.rect.x
                dy = self.target_player_pos['y'] - self.rect.y
                total_distance = math.hypot(dx, dy)
                if total_distance > 0:
                    self.direction.x = dx / total_distance
                    self.direction.y = dy / total_distance
        elif self.state == 'charging':
            self.charge(walls)
            player_pos = player_positions.get(self.target_player_id)
            if player_pos and self.rect.colliderect(pygame.Rect(player_pos['x'], player_pos['y'], 40, 40)):
                self.attack(self.target_player_id, send_damage_callback)
                self.state = 'idle'
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def charge(self, walls=None):
        self.move(self.direction.x * self.charge_speed, self.direction.y * self.charge_speed, walls)