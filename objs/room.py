from objs.world import World
import threading
import time
import json

room_id = 0


class Room:

    def __init__(self):
        global room_id
        self.id = room_id
        room_id += 1
        self.world = World("艾泽拉斯", room=self)
        self.clients = []
        self.start_flag = False

    def add_robot(self, client=None):
        new_country = self.world.create_country("", area=15, money=10, client=client)
        for _ in range(0, 10):
            self.world.create_person(new_country)
        return new_country

    def add_human(self, name, client):
        new_country = self.world.create_country(
            name, area=15, money=10, manual=True, client=client)
        for _ in range(0, 10):
            self.world.create_person(new_country)
        return new_country

    def start_async(self):
        threading._start_new_thread(self.start, ())

    def start_broadcast(self):
        threading._start_new_thread(self.status_publisher, ())

    def start(self):
        self.start_flag = True
        while True:
            self.broadcast("system", {
                "info": "游戏开始",
            })
            self.world.play()

    def status_publisher(self):
        while len(self.clients) != 0:
            self.broadcast("players", {
                "players": [country.to_json() for country in self.world.countrys]
            })
            self.broadcast("turn", {
                "country": self.world.current_turn
            })
            self.broadcast("world_info", self.world.to_json())
            if self.start_flag:
                self.broadcast("game", {
                    "info": "start"
                })
            time.sleep(1)

    def broadcast(self, channel, msg):
        for client in self.clients:
            client.sendMessage(json.dumps({
                "type": "broadcast",
                "channel": channel,
                "message": msg
            }, indent=4))
