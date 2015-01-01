arq1="daily_team_summary.txt.bz2"
arq2="daily_user_summary.txt.bz2"
for arquivo in "$arq1" "$arq2"
do
   modTime=$(ls -l $arquivo --time-style=long-iso | grep -oE [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]][0-9]{2}:[0-9]{2})
   resultado=1
   while [ $resultado -eq 1 ]
   do
      wget --wait=5 --random-wait --verbose --output-file="$arquivo".log --timestamping  --directory-prefix=/folding/arquivos fah-web.stanford.edu/"$arquivo"
      if [ $? -eq 0 ]
      then
         modTime1=$(ls -l $arquivo --time-style=long-iso | grep -oE [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]][0-9]{2}:[0-9]{2})
         let resultado=0
         if [ "$modTime" = "$modTime1" ]
         then
            let resultado=1
            sleep 30
         else
            bzip2 -t /folding/arquivos/"$arquivo"
            if [ $? -ne 0 ]
               then
               sleep 10
               let resultado=1
            fi
         fi
      fi
   done
done
