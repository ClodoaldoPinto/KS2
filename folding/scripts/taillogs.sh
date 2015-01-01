#!/bin/bash
cd /folding/scripts
tail -n 50000 kakaoStats.log > tmpfile
cat tmpfile > kakaoStats.log
tail -n 5000 folding.sql.Err.log > tmpfile
cat tmpfile > folding.sql.Err.log
rm tmpfile
