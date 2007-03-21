import bluetooth
import os

trusted = []
passwd = u"p"

s = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
port = bluetooth.get_available_port( bluetooth.RFCOMM )
s.bind(("",port))
s.listen(1)
uuid = "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
bluetooth.advertise_service(s, "controlblue", uuid,[bluetooth.SERIAL_PORT_CLASS],[bluetooth.SERIAL_PORT_PROFILE])
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
