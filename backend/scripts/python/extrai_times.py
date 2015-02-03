fi = open('fahstats_data_utf-8.dump', 'r')
fo = open('times_data.dump', 'w')
b = False
while True:
  line = fi.readline()
  if line.find('COPY times') > -1:
      while True:
          fo.write(line)
          line = fi.readline()
          if line.find('COPY times_indice') > -1:
              b = True
              break
      if b:
          break
fi.close()
fo.close()

