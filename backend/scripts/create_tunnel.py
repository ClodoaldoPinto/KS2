import os
import signal
import time

ip0 = ''
pid = -1
f = open('/var/www/html/db_ip/db_ip.txt', 'r')

while True:
   f.flush()
   f.seek(0)
   ip = f.readline().rstrip('\n')
   if ip0 != ip:
      if pid > -1:
         os.kill(pid, signal.SIGTERM)
         os.waitpid(pid, 0)
      pid = os.spawnl(
         os.P_NOWAIT, '/usr/bin/ssh', 'ssh', ip, '-nNCT', 
         '-o StrictHostKeyChecking no', '-L 5433:localhost:5432')
   ip0 = ip
   time.sleep(5)
