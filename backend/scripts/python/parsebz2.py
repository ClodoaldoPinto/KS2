#! /usr/bin/env python
import bz2, sys, re
import os.path as path

re_linha = re.compile(
  r'^(?P<name>[\041-\377]+)\t(?P<points>\d+(?:\.\d+)?)\t(?P<wus>\d+(?:\.\d+)?)\t(?P<team>\d{1,9})$'
  )
files_path = path.join(path.dirname(path.realpath(__file__)), '../../files')
fout = open(path.join(files_path, 'daily_user_summary_out.txt'), 'w')
foutData = open(path.join(files_path, 'data_usuarios.txt'), 'w')
fin = bz2.BZ2File(path.join(files_path, 'daily_user_summary.txt.bz2'), 'r')
foutData.write(fin.readline())
foutData.close()
fin.readline()
lines = 0
while True:
    linha = fin.readline()
    if linha == '':
        break
    m = re_linha.search(linha)
    if m:
        lines += 1
        fout.write('\t'.join((
            m.group('name')[:100],
            m.group('points'),
            str(int(m.group('wus'))),
            m.group('team')
            )) + '\n')
fin.close()
fout.close()
if lines < 500000:
    sys.exit('only %d lines in file daily_user_summary.txt.bz2' % lines)

fout = open(path.join(files_path, 'daily_team_summary_out.txt'), 'w')
fin = bz2.BZ2File(path.join(files_path, 'daily_team_summary.txt.bz2'))
fin.readline()
fin.readline()
lines = 0
while True:
    linha = fin.readline()
    if linha == '':
      break
    if len(linha) < 4:
      continue
    lines += 1
    linha = linha.replace('\r', '')
    column = linha.split('\t')
    if column[0] == '0':
      column[1] = 'Default'
    column[1] = column[1].strip()[:100]
    column[2] = str(long(round(float(column[2]))))
    fout.write('\t'.join(column))
fin.close()
fout.close()
if lines < 20000:
   sys.exit('only %d lines in file daily_team_summary.txt.bz2' % lines)
