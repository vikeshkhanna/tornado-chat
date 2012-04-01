import tornado.ioloop
import tornado.web
from tornado import template, websocket

GLOBALS = {
	"sockets" : [],
	"users" : [],
	"TEMPLATE_ROOT" : ""
}

class HomeHandler(tornado.web.RequestHandler):
	def get(self):
		loader = template.Loader(GLOBALS['TEMPLATE_ROOT'])
		self.write(loader.load("chat-client-login.html").generate())

class ChatHandler(tornado.web.RequestHandler):
	def get(self):
		pass

	def post(self):
		username = self.get_argument('username')		
		loader = template.Loader(GLOBALS['TEMPLATE_ROOT'])
		self.write(loader.load("chat-client-main.html").generate(username=username))
	
class ClientSocket(websocket.WebSocketHandler):
	def open(self):
		username = self.get_argument('username').replace("'","")
		GLOBALS['sockets'].append(self)
		GLOBALS['users'].append(username)
		
		for socket in GLOBALS['sockets']:
			socket.write_message(username + " joined the room!")

		print "WebSocket opened for user " + username
		
	def on_message(self, message):
		sender = GLOBALS['users'][GLOBALS['sockets'].index(self)]

		for i in range(len(GLOBALS['sockets'])):
			username = GLOBALS['users'][i]
			socket = GLOBALS['sockets'][i] 	
			socket.write_message(sender +  " : " + message)

	def on_close(self):
		index = GLOBALS['sockets'].index(self)
		username = GLOBALS['users'][index]
		GLOBALS['sockets'].remove(self)
		del GLOBALS['users'][index]
		
		for socket in GLOBALS['sockets']:
			socket.write_message(username + " left the room!")

		print "WebSocket removed for user " + username

class Announcer(tornado.web.RequestHandler):
	def get(self):
		data = self.get_argument('data')
		
		for socket in GLOBALS['sockets']:
			socket.write_message(data)
	
		self.write('Posted')

application = tornado.web.Application([(r"/", HomeHandler),
				       (r"/chat", ChatHandler),
				       (r"/socket", ClientSocket),
				       (r"/push", Announcer)])

if __name__ == "__main__":
	print("running server at localhost 8888")
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()


