# entities/player.py

import pygame
from entities.entity import Entity
from entities.inventory import Inventory
from network.client import send_message  # Asegúrate de que send_message está disponible

class Player(Entity):
    def __init__(self, x, y, on_death_callback=None):
        super().__init__(x, y, 40, 40)
        self.base_image = pygame.Surface((40, 40))
        self.base_image.fill((255, 0, 0))  # Rojo para el jugador
        self.image = pygame.image.load('assets/prota.png')
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.name = "Jugador"
        self.inventory = Inventory()
        self.weapon = None  # Arma equipada
        self.on_death_callback = on_death_callback  # Callback para manejar la muerte

    def move(self, keys, walls):
        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_s]:
            dy = self.speed
        if keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_d]:
            dx = self.speed

        # Intentar mover en X
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:  # Moviendo a la derecha
                    self.rect.right = wall.left
                elif dx < 0:  # Moviendo a la izquierda
                    self.rect.left = wall.right
                break

        # Intentar mover en Y
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:  # Moviendo hacia abajo
                    self.rect.bottom = wall.top
                elif dy < 0:  # Moviendo hacia arriba
                    self.rect.top = wall.bottom
                break

    def attack(self, enemies):
        # Ataque cuerpo a cuerpo o con arma
        damage = 25
        if self.weapon and self.weapon.type == 'weapon':
            damage = self.weapon.effect  # Suponemos que el efecto es el daño
        for enemy_id, enemy in enemies.items():
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < 50:
                # Enviar mensaje al servidor para atacar al enemigo
                send_message({
                    'attack': {
                        'enemy_id': enemy_id,
                        'damage': damage
                    }
                })
                break  # Solo atacamos a un enemigo a la vez

    def receive_damage(self, amount):
        self.health -= amount
        print(f"Has recibido {amount} puntos de daño. Salud restante: {self.health}")
        if self.health <= 0:
            self.game_over()

    def update_image(self):
        self.image = pygame.image.load('assets/prota.png')
        if self.weapon:
            # Superponer la imagen del arma
            weapon_image = pygame.image.load(self.weapon.image_path).convert_alpha()
            self.image.blit(weapon_image, (-2, -5))  # Ajusta la posición según sea necesario
            
    def game_over(self):
        print("¡Has sido derrotado!")
        if self.on_death_callback:
            self.on_death_callback()
