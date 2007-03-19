import e32, socket, appuifw

CONFIG_DIR = 'e:/controlblue'
CONFIG_FILE=os.path.join(CONFIG_DIR, 'commandlist.txt')

class BlueToothError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Computer:
  def __init__(self, servicename):
    try:
      address,services = socket.bt_discover()
    except:
      raise BlueToothError("No services found")
    else:
      if unicode(servicename) in services:
	self.address = address
	self.portno = services[unicode(servicename)]
      else:
	raise BlueToothError("No services found")

  def connect(self):
    self.s = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
    self.s.connect((self.address, self.portno))

  def send(self, data):
    self.connect()
    self.s.send(unicode(data))
    self.close()

  def close(self):
    self.s.close()

class commandList:
  commands = [u"Empty..."]
  isEmpty = True

  def __init__(self, computer):
    self.computer = computer
  
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
    self.computer.send(self.commands[index])

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
  mycommands = commandList(Computer("controlblue"))
  appuifw.app.screen = 'normal'
  appuifw.app.title = u"controlBlue"
  mycommands.read()
  appuifw.app.body = mycommands.lb
  appuifw.app.exit_key_handler = exit_key_handler
  appuifw.app.menu = [(u'New', mycommands.newCmd), (u'Edit', mycommands.editCmd), (u'Delete', mycommands.remCmd)]
  app_lock = e32.Ao_lock()
  app_lock.wait()
except BlueToothError, inst:
  print inst.value
