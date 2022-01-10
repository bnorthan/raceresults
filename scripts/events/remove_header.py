
import re

years=[2012,2013,2014,2015,2016]
encoding=None

time_pattern='(?:[1-2]:)?[0-5][0-9]:[0-5][0-9]' 

def get_lines(file):
    with open(file,encoding=encoding) as f:
        lines = f.readlines()
    return lines

for year in years:
    file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/from_are/'+str(year)+'_.txt'
    out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'

    lines=get_lines(file)
    lines_=[]
    for line in lines:
        print(line)
        times=re.findall(time_pattern, line)
        if (len(times)>0):
            lines_.append(line)

    #for line in lines:
    with open(out_file,'w') as f:
        f.writelines(lines_)



