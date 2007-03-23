import e32, socket, appuifw, key_codes

CONFIG_DIR = 'e:/controlblue'
CONFIG_FILE=os.path.join(CONFIG_DIR, 'commandlist.txt')
CONFIG_FILE_KEYS=os.path.join(CONFIG_DIR, 'keybindings.txt')
SERVICE_NAME = "controlblue"
KEYCODES = [key_codes.EKey0, key_codes.EKey1, key_codes.EKey2, key_codes.EKey3, key_codes.EKey4, key_codes.EKey5, key_codes.EKey6, key_codes.EKey7, key_codes.EKey8, key_codes.EKey9]

class BlueToothError(Exception):
  def __init__(self, value):
    self.value = value
    appuifw.note(value, 'error')
  def __str__(self):
    return repr(self.value)

class Computer:
  def __init__(self):
    self.address = None
    try:
      self.discover()
    except BlueToothError:
      pass

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
      self.address = None
      raise BlueToothError(SERVICE_NAME + u' is not running on selected device')

  def auth(self):
    if (not self.address):
      appuifw.note (u'Not connected!', 'error')
      return False
    passwd = appuifw.query(u'Authentication required. Enter password', 'code')
    while (passwd):
      try:
       result = self.send(u"pass " + passwd)
      except socket.error, inst:
	appuifw.note(u'Unable to connect!', 'error')
	return False
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
    try:
      result = self.send(data)
    except socket.error, inst:
      appuifw.note(u"Unable to connect!", 'error')
      return
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

  def __init__(self):
    self.initKeys()

  def initKeys(self):
    self.keys = self.initList([], lambda i: None)

  def initList(self, l, g):
    for i in range(10):
      l.append(g(i))
    return l
      

  def read(self):
    try:
      f = open (CONFIG_FILE, 'rt')
      try:
	content = eval(f.read()) #format is (names, commands, keys)
	self.commandNames = eval(content[0])
	self.commands = eval(content[1])
	self.keys = eval(content[2])
	
	if (self.commandNames == []):
	  self.isEmpty = True
	  self.commandNames = [u"Empty..."]
	  self.commands = {}
	  self.initKeys()
	else:
	  self.isEmpty = False
	f.close()
      except:
	appuifw.note(u"Unable to read file", "error")
	self.isEmpty = True
	self.commandNames = [u"Empty..."]
	self.commands = {}
	self.initKeys()
    except:
      self.isEmpty = True
      self.commandNames = [u"Empty..."]
      self.commands = {}
      self.initKeys()
    self.lb = appuifw.Listbox(self.commandNames, self.callback)
    print self.keys
  
  def write(self):
    if (self.isEmpty):
      self.commandNames = []
    if not os.path.isdir(CONFIG_DIR):
      os.makedirs(CONFIG_DIR)
    f = open (CONFIG_FILE, 'wt')
    try:
      data = (repr(self.commandNames), repr(self.commands), repr(self.keys))
      f.write(repr(data))
    except:
      appuifw.note(u"Unable to write to file", "error")
    f.close()

  def callback(self):
    if (self.isEmpty):
      return
    key = self.commandNames[self.lb.current()]
    mycomputer and mycomputer.sendCommand(self.commands[key])

#figure out how user can cancel form
  def run_form(self, name = '', cmd = '', hotkey = 0, pos = 0):
    data = [(u'Name', 'text', unicode(name)), (u'Command', 'text', unicode(cmd)), (u'Hotkey', 'combo', (self.initList([u'None'], lambda x: unicode(x)), hotkey))]
    t = True
    while (t):
      f = appuifw.Form(data, appuifw.FFormEditModeOnly)
      f.execute()
      data = f
      if ((f[0][2]).strip() == u''):
	if appuifw.query(u'Name cannot be blank! Try again?'):
	  data[0][2] = name
	else:
	  t = False
      elif ((f[1][2]).strip() == u''):
	if appuifw.query(u'Command cannot be blank! Try again?'):
	  data[1][2] = cmd
	else:
	  t = False
      elif ((f[0][2]).strip() in self.commandNames):
	if appuifw.query(u'Cant have two commands with same name! Try again?'):
	  data[0][2] = name
	else:
	  t = False
      else:
	t= False  
    newname = (f[0][2]).strip()
    newcmd = (f[1][2]).strip()
    newhotkey = f[2][2][1] -1  #since 0 is "None"
    if (self.isEmpty):
      self.commandNames = []
      self.commands = {}
      self.isEmpty = False
    self.commandNames.insert(pos, newname)
    self.commands[newname] = newcmd
    if (newhotkey != -1):
      self.keys[newhotkey] = newname
      self.lb.bind(KEYCODES[newhotkey], lambda: self.handle_key(newhotkey))
    else:
      self.lb.bind(KEYCODES[newhotkey], None)
    self.lb.set_list(self.commandNames)
  
  def newCmd(self):
    self.run_form()

  def remCmd(self):
    if (self.isEmpty):
      return
    if (not appuifw.query(u'Delete command?')):
      return
    index = self.lb.current()
    self.rem_aux(index)

  def rem_aux(self, index):
    key = self.commandNames[index]
    del self.commandNames[index]
    del self.commands[key]
    if (key in self.keys):
      self.lb.bind(KEYCODES[self.keys.index(key)], None) #unbind
      self.keys.remove(key)

    if (self.commandNames == []):
      self.isEmpty = True
      self.commandNames = [u'Empty...']
      self.commands = {}

    self.lb.set_list(self.commandNames)

#will change completely
  def editCmd(self):
    if (self.isEmpty):
      return
    i = self.lb.current()
    name = self.commandNames[i]
    cmd = self.commands[name]
    if (name in self.keys):
      hotkey = self.keys.index(name) + 1 #coz 0th is 'None'
    else:
      hotkey = 0

    self.rem_aux(i)
    self.run_form(name, cmd, hotkey, i)

  def handle_key(self, i):
    print "test"
    print i
    if (self.keys[i] != None):
      mycomputer.sendCommand(self.commands[self.keys[i]])

  def bind_keys(self):
    for i in range(10):
      if (self.keys[i] != None):
	self.lb.bind(KEYCODES[i], (lambda x: lambda: self.handle_key(x))(i))

  def unbind_keys(self):
    for i in range(10):
      self.lb.bind(KEYCODES[i], None)

def exit_key_handler():
  mycommands.write()
  app_lock.signal()

mycomputer = Computer()
mycommands = commandList()

MENU_LIST = [(u'New', mycommands.newCmd), (u'Edit', mycommands.editCmd), (u'Delete', mycommands.remCmd), (u'Connection', ((u'Reconnect', mycomputer.discover), (u'Authenticate', mycomputer.auth)))]

appuifw.app.screen = 'normal'
appuifw.app.title = u"controlBlue"
mycommands.read()
mycommands.bind_keys()
appuifw.app.body = mycommands.lb
appuifw.app.exit_key_handler = exit_key_handler
appuifw.app.menu = MENU_LIST
app_lock = e32.Ao_lock()
app_lock.wait()
