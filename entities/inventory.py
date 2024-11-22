# entities/inventory.py
from network.client import send_message
class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        print(f"Has obtenido: {item.name}")

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def use_item(self, item, player):
        if item in self.items:
            item.apply_effect(player)
            self.remove_item(item)
            if item.type == 'weapon':
                # Informar a los demás jugadores que hemos equipado un arma
                send_message({'equip': {'weapon_name': item.name}})