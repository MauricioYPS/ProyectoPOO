from game_object import GameObject
import pygame
import math
from weapon.weapon import Weapon
from weapon.weapon import Pistol
class Player(GameObject):
    def __init__(self, x, y, width=32, height=32, speed=200, image=None):
        super().__init__(x, y, width, height, image)
        self.speed = speed
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))
        self.bullets = []
        self.health = 100
        self.invincible = False
        self.invincible_time = 0

        # Equipar un arma básica al inicio
        self.current_weapon = Pistol(x, y)
        print(f"Arma inicial equipada: {self.current_weapon.name}")

    def handle_input(self, game_map, delta_time):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -self.speed * delta_time
        if keys[pygame.K_s]:
            dy = self.speed * delta_time
        if keys[pygame.K_a]:
            dx = -self.speed * delta_time
        if keys[pygame.K_d]:
            dx = self.speed * delta_time

        new_x = self.x + dx
        new_y = self.y + dy
        if game_map.is_walkable(new_x, self.y):
            self.x = new_x
        if game_map.is_walkable(self.x, new_y):
            self.y = new_y

    def shoot(self, target_x, target_y):
        
        if self.current_weapon is None:
            print("Intento de disparo sin arma equipada.")
            return
        
        if self.current_weapon:
            # Calcular la dirección de la bala
            direction_x = target_x - (self.x + self.width // 2)
            direction_y = target_y - (self.y + self.height // 2)
            distance = math.sqrt(direction_x**2 + direction_y**2)
            if distance > 0:
                direction_x /= distance
                direction_y /= distance

            # Crear la bala con daño del arma equipada
            bullet = pygame.Rect(self.x + self.width // 2, self.y + self.height // 2, 5, 5)
            self.bullets.append((bullet, direction_x, direction_y, self.current_weapon.damage))
            print(f"Bala agregada: {self.bullets[-1]}")  # Depuración


    def update_bullets(self, delta_time, game_map):
        """
        Actualiza las balas activas.
        """
        new_bullets = []
        for bullet, dx, dy, damage in self.bullets:
            # Mover la bala
            bullet.x += dx * 300 * delta_time
            bullet.y += dy * 300 * delta_time

            # Detectar colisión con barriles
            if game_map.check_barrel_collision(bullet):
                print("Bala impactó un barril y fue eliminada.")
                continue  # No añadir esta bala a la lista de nuevas balas

            # Detectar colisión con enemigos
            for enemy in game_map.enemies[:]:
                if bullet.colliderect(enemy.rect):
                    print(f"Bala impactó a un enemigo con {damage} de daño.")
                    if enemy.receive_damage(damage):
                        game_map.enemies.remove(enemy)
                    break
            else:
                # Si no hubo colisión, mantener la bala
                new_bullets.append((bullet, dx, dy, damage))

        self.bullets = new_bullets



    def draw_bullets(self, screen, offset_x, offset_y):
        for bullet, _, _, _ in self.bullets:
            pygame.draw.rect(screen, (255, 255, 0), (bullet.x - offset_x, bullet.y - offset_y, bullet.width, bullet.height))


    def receive_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_time = 1.5

    def update_invincibility(self, delta_time):
        if self.invincible:
            self.invincible_time -= delta_time
            if self.invincible_time <= 0:
                self.invincible = False

    def pick_up_weapon(self, weapon):
        if isinstance(weapon, Weapon):
            self.current_weapon = weapon
        else:
            print("El ítem recogido no es un arma.")


