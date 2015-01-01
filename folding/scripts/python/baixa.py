#! /usr/bin/env python

import pycurl, StringIO, re, time, os, subprocess, sys

def seconds_since(start):

   return time.time() - start

def std_out(message=''):

   print message
   sys.stdout.flush()

def time_str2int(strtime):

   try:
      time_tuple = time.strptime(strtime, '%a, %d %b %Y %H:%M:%S %Z')
   except ValueError:
      time_tuple = (1900, 1, 1, 0, 0, 0, 0, 1, -1)
   return int(time.mktime(time_tuple))

def aguarda_update(url, file_path):

   time_start = time.time()
   try:
      file_mtime = os.stat(file_path)[8]
   except OSError:
      file_mtime = 0

   while True:
      b = StringIO.StringIO()
      c = pycurl.Curl()
      c.setopt(pycurl.URL, url)
      c.setopt(pycurl.HEADER, True)
      c.setopt(pycurl.NOBODY, True)
      c.setopt(pycurl.WRITEFUNCTION, b.write)
      c.setopt(pycurl.TIMEOUT, 50)
      c.setopt(pycurl.CONNECTTIMEOUT, 50)
      c.perform()
      sio = b.getvalue()
      b.seek(0)
      b.truncate()
      pat = r'^Last-Modified:\s*(.*)$'
      last_modified = (re.findall(pat, sio, re.M + re.I)[0]).strip()
      last_modified = time_str2int(last_modified)
      std_out('Now:\t%s\nLast modified:\t%s\nFile mtime:\t%s\n' % (
            time.asctime(time.gmtime()),
            time.asctime(time.localtime(last_modified)),
            time.asctime(time.localtime(file_mtime))
            ))
      b.close()
      c.close()
      std_out()
      if last_modified > file_mtime:
         break
      time_now = time.time()
      if time_now - time_start > 30 * 60:
         sys.exit(1)
      time.sleep(10)

   std_out("""
%s
HEAD
Time: %s
File time: %s
Last modified: %s
Difference min: %s
""" % (sio, time.ctime(), file_mtime, last_modified,
      (last_modified - file_mtime) / 60))

   pat = r'^Content-Length:\s*(.*)$'
   size = int((re.findall(pat, sio, re.M + re.I)[0]).strip())
   return size, last_modified

def get_file(size, url):

   if size < 50000: chunk_number = 1
   elif size < 1024 * 1024: chunk_number = 2
   else: chunk_number = 6
   chunk_size = size / chunk_number

   m = pycurl.CurlMulti()
   c = list()
   b = list()
   for i in range(chunk_number):
      start = chunk_size * i
      if i < chunk_number -1:
         end = start + chunk_size -1
      else:
         end = ''
      b.append(StringIO.StringIO())
      c.append(pycurl.Curl())
      c[i].setopt(pycurl.HTTPHEADER, ['Range: bytes=%s-%s' % (start, end)])
      c[i].setopt(pycurl.URL, url)
      c[i].setopt(pycurl.WRITEFUNCTION, b[i].write)
      m.add_handle(c[i])

   sleep_seconds = 0.5
   seconds_limit = 12 * 60
   start = time.time()
   std_out('get_file() start: %s' % time.ctime())

   while (seconds_since(start) < seconds_limit):

      ret, num_handles = m.perform()
      std_out('Loop 0. ret: %s, num_handles: %s' % (ret, num_handles))
      if ret != pycurl.E_CALL_MULTI_PERFORM: break
      time.sleep(sleep_seconds)

   std_out('Fim do loop 0 %s' % time.ctime())

   while num_handles and (seconds_since(start) < seconds_limit):

      ret = m.select(10.0)
      std_out('Loop 1,0. ret: %s, num_handles: %s' % (ret, num_handles))
      time.sleep(sleep_seconds)
      if ret == -1: continue

      while True:

         ret, num_handles = m.perform()
         std_out('Loop 1,1. ret: %s, num_handles: %s' % (ret, num_handles))
         if ret != pycurl.E_CALL_MULTI_PERFORM: break
         std_out('time.sleep(%s)' % (sleep_seconds / 2))
         time.sleep(sleep_seconds / 2)

   m.close()

   total_time = time.time() - start

   std_out("""
GET
Time: %s
URL: %s
Chunks: %s
Download size: %s
Total time seconds: %.2f
KBytes/s: %.2f
""" % (time.ctime(), url, chunk_number, size,
      total_time, size / total_time / 1024))

   return ''.join((x.getvalue() for x in b))

def download(server, file_name, file_dir):

   while True:

      file_path = os.path.join(file_dir, file_name)
      url = 'http://%s/%s' % (server, file_name)
      size, last_modified = aguarda_update(url, file_path)
      sio = get_file(size, url)
      open(file_path, 'wb').write(sio)
      os.utime(file_path, (last_modified, last_modified))
      std_out('file size: %s download_size: %s difference: %s' \
         % (size, len(sio), size - len(sio)))
      retcode = subprocess.call(['bzip2', '-t', file_path])
      if retcode == 0: break
      std_out('\n%sCorrupted file%s\n' % (('*' * 5,) * 2))
      os.unlink(file_path)

   std_out('%s%s%s' % ('\n', '-' * 40, '\n'))

def main():

   file_dir = '/folding/arquivos'
   log_file_time = time.strftime('%y-%m-%d_%H:%M:%S', time.gmtime())
   sys.stderr = open(os.path.join(file_dir,'download.log_%s' % log_file_time), 'wb')
   sys.stdout = sys.stderr
   #server = 'fah-web.stanford.edu'
   server = 'kakaostats.com/summary_files'

   file_name = 'daily_team_summary.txt.bz2'
   download(server, file_name, file_dir)

   file_name = 'daily_user_summary.txt.bz2'
   download(server, file_name, file_dir)

   sys.stderr.close()

main()
