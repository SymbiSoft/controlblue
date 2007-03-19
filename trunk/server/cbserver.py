from lightblue import *
import os

s = socket()
s.bind(("", 0))
s.listen(1)
advertise("controlblue", s, RFCOMM)
data = ""
while data != "exit":
  conn, addr = s.accept()
  data = conn.recv(1024)
  conn.close()
  (data != "exit") and os.system(data) 
s.close()
