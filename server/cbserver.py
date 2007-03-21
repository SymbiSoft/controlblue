from lightblue import *
import bluetooth
import os

trusted = []
passwd = u"p"

s = socket()
s.bind(("", 0))
s.listen(1)
advertise("controlblue", s, RFCOMM)
data = ""
while data != "exit":
  conn, addr = s.accept()
  data = conn.recv(1024)
  if (addr in trusted):
    (data != "exit") and os.system(data)
    conn.send(u'1') #3 is sent if operation is not allowed
  elif ((data[0:4] == u'pass') and (data[5:] == passwd)):
    trusted.append(addr)
    conn.send(u"1")
  else:
    conn.send(u"0")
  conn.close()
s.close()
