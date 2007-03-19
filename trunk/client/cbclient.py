import e32, socket, appuifw

CONFIG_DIR = 'e:/controlblue'
CONFIG_FILE=os.path.join(CONFIG_DIR, 'commandlist.txt')
SERVICE_NAME = "controlblue"

class BlueToothError(Exception):
  def __init__(self, value):
    self.value = value
    appuifw.note(value, 'error')
  def __str__(self):
    return repr(self.value)

class Computer:
  def __init__(self):
    self.address = None
    self.discover()

  def discover(self):
    try:
      address,services = socket.bt_discover()
    except:
      self.address = None
      raise BlueToothError(u'Not connected')
    if unicode(SERVICE_NAME) in services:
      self.address = address	
      self.portno = services[unicode(SERVICE_NAME)]
      self.auth() or appuifw.note(u'Authentication failed!', 'error')
    else:
      appuifw.note(u'shit')
      self.address = None
      raise BlueToothError(SERVICE_NAME + u' is not running on selected device')

  def auth(self):
    appuifw.note(u'noshit')
    if (not self.address):
      appuifw.note (u'Not connected!', 'error')
      return False
    passwd = appuifw.query(u'Authentication required. Enter password', 'code')
    while (passwd):
      result = self.send(u"pass " + passwd)
      if (result == u'0'):
	passwd =  appuifw.query(u'Incorrect password! Try again', 'code')
      else:
	return True
    return False
  
  def connect(self):
    self.s = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
    self.s.connect((self.address, self.portno))

  def send(self, data):
    self.connect()
    self.s.send(unicode(data))
    result = self.s.recv(4)
    self.close()
    return result

  def sendCommand(self, data):
    if (not self.address):
      try:
	self.discover()
      except BlueToothError, inst:
	return
    result = self.send(data)
    if (result == u'0'):
      if (self.auth()):
	self.send(data)
      else:
	appuifw.note(u'Authentication failed!', 'error')
	return
    if (result == u'3'):
      appuifw.note(u'This operation is not allowed!', 'error')

  def close(self):
    self.s.close()

class commandList:
  commands = [u"Empty..."]
  isEmpty = True
  
  def read(self):
    try:
      f = open (CONFIG_FILE, 'rt')
      try:
	content = f.read()
	self.commands = eval(content)
	self.isEmpty = False
	f.close()
      except:
	appuifw.note(u"Unable to read file", "error")
	self.isEmpty = True
	self.commands = [u"Empty..."]
    except:
      self.isEmpty = True
      self.commands = [u"Empty..."]
    self.lb = appuifw.Listbox(self.commands, self.callback)
  
  def write(self):
    if (self.isEmpty):
      return
    if not os.path.isdir(CONFIG_DIR):
      os.makedirs(CONFIG_DIR)
    f = open (CONFIG_FILE, 'wt')
    try:
      f.write(repr(self.commands))
    except:
      appuifw.note(u"Unable to write to file", "error")
    f.close()

  def callback(self):
    if (self.isEmpty):
      return
    index = self.lb.current()
    mycomputer and mycomputer.sendCommand(self.commands[index])

  def newCmd(self):
    data = appuifw.query(u"Enter command", "text")
    if (self.isEmpty):
      self.commands = []
      self.isEmpty = False
    self.commands.append(data)
    self.lb.set_list(self.commands)
  
  def remCmd(self):
    if (self.isEmpty):
      return
    del self.commands[self.lb.current()]
    self.lb.set_list(self.commands)

  def editCmd(self):
    if (self.isEmpty):
      return
    cmd = self.commands[self.lb.current()]
    cmd = appuifw.query(u"Edit Command:", 'text', cmd)
    

def exit_key_handler():
  mycommands.write()
  app_lock.signal()

try:
  mycomputer = Computer()
except BlueToothError:
  pass
mycommands = commandList()

MENU_LIST = [(u'New', mycommands.newCmd), (u'Edit', mycommands.editCmd), (u'Delete', mycommands.remCmd), (u'Connection', ((u'Reconnect', mycomputer.discover), (u'Authenticate', mycomputer.auth)))]

appuifw.app.screen = 'normal'
appuifw.app.title = u"controlBlue"
mycommands.read()
appuifw.app.body = mycommands.lb
appuifw.app.exit_key_handler = exit_key_handler
appuifw.app.menu = MENU_LIST
app_lock = e32.Ao_lock()
app_lock.wait()
