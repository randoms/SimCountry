import web
from objs.room import Room
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import threading
import json
import uuid

urls = (
    '/', 'index',
    '/room/create', 'create_room',
)

room_list = []


# http server

class create_room:
    def GET(self):
        global room_list
        

class room:
    def GET(self):
        pass

class index:
    def GET(self):
        return "Hello, world!"


# websocker server

ws_clients = []
req_records = {}

class SimpleEcho(WebSocket):

    def handleMessage(self):
        global room_list, req_records
        msg = json.loads(self.data)
        print(self.data)
        try:
            if "type" in msg and msg['type'] == "request":
                if msg["message"]["url"] == "create_room":
                    new_room = Room()
                    room_list.append(new_room)
                    new_room.clients.append(self)
                    self.sendMessage(json.dumps({
                        'type': 'response',
                        'req_id': msg['req_id'],
                        'message': {
                            'room': {
                                'id': new_room.id
                            }
                        }
                    }, indent=4))
                    new_room.start_broadcast()

                if msg["message"]["url"] == "join_room":
                    room_id = (int)(msg["message"]['room_id'])
                    target_room = list(filter(lambda room: room.id == room_id, room_list))[0]
                    target_room.clients.append(self)
                    self.sendMessage(json.dumps({
                        'type': 'response',
                        'req_id': msg['req_id'],
                        'message': {
                            'room': {
                                'id': target_room.id
                            }
                        }
                    }, indent=4))

                if msg["message"]["url"] == "create_country":
                    room_id = (int)(msg["message"]['room_id'])
                    target_room = list(filter(lambda room: room.id == room_id, room_list))[0]
                    country_name = msg["message"]["country_name"]
                    new_country = target_room.add_human(country_name, self)
                    self.sendMessage(json.dumps({
                        'type': 'response',
                        'req_id': msg['req_id'],
                        'message': {
                            'country': new_country.to_json()
                        }
                    }, indent=4))

                if msg["message"]["url"] == "add_robot":
                    room_id = (int)(msg["message"]['room_id'])
                    target_room = list(filter(lambda room: room.id == room_id, room_list))[0]
                    new_country = target_room.add_robot(client=self)
                    
                    self.sendMessage(json.dumps({
                        'type': 'response',
                        'req_id': msg['req_id'],
                        'message': {
                            'country': new_country.to_json()
                        }
                    }, indent=4))
                
                if msg["message"]["url"] == "start_game":
                    room_id = (int)(msg["message"]['room_id'])
                    target_room = list(filter(lambda room: room.id == room_id, room_list))[0]
                    target_room.start_async()
                    self.sendMessage(json.dumps({
                        'type': 'response',
                        'req_id': msg['req_id'],
                        'message': {
                            'room': {
                                'id': target_room.id
                            }
                        }
                    }, indent=4))

            if "type" in msg and msg["type"] == "response":
                if msg["req_id"] in req_records and req_records[msg["req_id"]] is not None:
                    req_records[msg["req_id"]](msg["message"])
                    req_records[msg["req_id"]] = None
        except Exception as e:
            print(e)
            

    def handleConnected(self):
        global ws_clients
        if self not in ws_clients:
            ws_clients.append(self)
        print(self.address, 'connected')

    def handleClose(self):
        global ws_clients
        if self in ws_clients:
            ws_clients.remove(self)
        print(self.address, 'closed')
    
    def send_request(self, message, cb):
        req_id = str(uuid.uuid1())
        req_records[req_id] = cb
        self.sendMessage(json.dumps({
            "type": "request",
            "req_id": req_id,
            "message": message
        }, indent=4))

def start_websocket_server():
    server = SimpleWebSocketServer('', 8000, SimpleEcho)
    server.serveforever()


if __name__ == "__main__":
    app = web.application(urls, globals())
    threading._start_new_thread(start_websocket_server, ())
    app.run()
