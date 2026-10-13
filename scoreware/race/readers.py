import glob
import re
import os
import pandas as pd
from scoreware.race.utils import get_last_name


def read_stockade_dates(csv_dir):
    """Real race dates from <csv_dir>/dates.csv (day, month, year) -> {year: date}.
    2022-2025 are inferred from the 2nd-Sunday-of-November pattern, not from an
    official source."""
    d = pd.read_csv(os.path.join(csv_dir, 'dates.csv'))
    dates = {}
    for _, r in d.iterrows():
        stamp = f"{int(r['year'])}-{str(r['month']).strip()}-{int(r['day'])}"
        dates[int(r['year'])] = pd.to_datetime(stamp).date()
    return dates


ALLTIME_COLUMNS = ['place', 'first_name', 'last_name', 'gender', 'age', 'city', 'state', 'time']

def read_alltime(csv_dir):
    """Every <year>.csv in the all-time Stockade set as one table, with year and
    race_date added.  Era differences are smoothed over: a column a year lacks
    comes back NaN, gender is 'M'/'F'/'u', and age is NaN unless it is a real age."""
    dates = read_stockade_dates(csv_dir)
    frames = []
    for f in sorted(glob.glob(os.path.join(csv_dir, '[12][0-9][0-9][0-9].csv'))):
        year = int(os.path.basename(f)[:4])
        df = pd.read_csv(f, dtype=str).reindex(columns=ALLTIME_COLUMNS)
        df.insert(0, 'year', year)
        df.insert(1, 'race_date', dates.get(year))
        frames.append(df)
    alltime = pd.concat(frames, ignore_index=True)

    gender = alltime['gender'].str.strip().str.upper().str[:1]
    alltime['gender'] = gender.where(gender.isin(['M', 'F']), 'u')
    # parsers fill a missing age with -1, 0 or 'none'
    age = pd.to_numeric(alltime['age'], errors='coerce')
    alltime['age'] = age.where(age.between(5, 99))
    return alltime

def parse_general(df, headers, id):
    
    newdf=pd.DataFrame()

    print((type(headers)))
    for key in headers:
        print((headers[key]))
        for column in df.columns:
            if column.lower().strip(' ') in headers[key]:
                print((column.lower().strip(' ')+' matches'))
                print(key)
                print(key=='name')

                #if (key=='time'):
                #    df[column]=df[column].replace('nan', method='bfill')
                #    df[column]=df[column].fillna(method='bfill')
                #    print((df[column].loc[1:10]))
                #    df[column]=df[column].astype(str)
                #    print((df[column].loc[230:240]))
                #    newdf['time']=df[column].apply(lambda x: '00:'+x.split(':')[0]+':'+x.split(':')[1])
                if (key=='full_name'):
                    df[column]=df[column].fillna(value='none none')
                    df[column]=df[column].replace('nan', value='none none')
                    df[column]=df[column].astype(str)
                    newdf['first_name']=df[column].apply(lambda x: x.split()[0])
                    
                    #newdf['last_name']=df[column].apply(lambda x: x.split()[-1])
                    newdf['last_name']=df[column].apply(lambda x: get_last_name(x))
                    print(newdf['last_name'])
                if (key=='lf_name'):
                    df[column]=df[column].fillna(value='none none')
                    df[column]=df[column].replace('nan', value='none none')
                    df[column]=df[column].astype(str)
                    newdf['last_name']=df[column].apply(lambda x: x.split()[0].strip(','))
                    
                    #newdf['last_name']=df[column].apply(lambda x: x.split()[-1])
                    newdf['first_name']=df[column].apply(lambda x: get_last_name(x))
                    print(newdf['last_name'])
                  
                else:
                    if (key=='time'):
                        df[column]=df[column].apply(lambda x: str(x).strip('*'))

                    if (key=='age'):
                        df[column]=df[column].fillna(value=-1)
                    else:
                        df[column]=df[column].fillna(value='none')
                    newdf[key]=df[column]

    newdf['race_id']=id

    return newdf

def parse_general2(df, headers, id):

    newdf=pd.DataFrame()

    print((type(headers)))
    for key in headers:
        print((headers[key]))
        for column in df.columns:
            if column.lower() in headers[key]:
                print((column.lower()+' matches'))
                print(key)
                print(key=='name')

                #if (key=='time'):
                #    df[column]=df[column].replace('nan', method='bfill')
                #    df[column]=df[column].fillna(method='bfill')
                #    print((df[column].loc[1:10]))
                #    df[column]=df[column].astype(str)                    
                #    #newdf['time']=df[column].apply(lambda x: '00:'+x.split(':')[0]+':'+x.split(':')[1])                
                if (key=='full_name'):
                    df[column]=df[column].fillna(value='none none')
                    df[column]=df[column].replace('nan', value='none none')
                    df[column]=df[column].astype(str)
                    newdf['first_name']=df[column].apply(lambda x: x.split()[0])
                    
                    #newdf['last_name']=df[column].apply(lambda x: x.split()[-1])
                    newdf['last_name']=df[column].apply(lambda x: raceutil.get_last_name(x))
                    print(newdf['last_name'])
                    
                else:
                    if (key=='age'):
                        df[column]=df[column].fillna(value=-1)
                    else:
                        df[column]=df[column].fillna(value='none')
                    newdf[key]=df[column]

    newdf['race_id']=id

    return newdf





def read_runscore(path):
    """A RunScore-style results text (as HMRRC posts them) -> DataFrame.

    Column positions come from the '===== ====...' line under the header, so a
    value that fills its column (a long name, a blank state) can't shift the
    others.  Only lines that start with a place number are kept; the title,
    record and footnote lines are dropped.
    """
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    sep = next(i for i, l in enumerate(lines) if l.strip().startswith('==='))
    spans = [m.span() for m in re.finditer(r'=+', lines[sep])]
    # a column's text can run to the start of the next one (gaps are 1-2 spaces)
    bounds = [(start, spans[i + 1][0] if i + 1 < len(spans) else None) for i, (start, _) in enumerate(spans)]
    header = [lines[sep - 1][a:b].strip() for a, b in bounds]
    rows = [[l[a:b].strip() for a, b in bounds] for l in lines[sep + 1:] if re.match(r'\s*\d+\s', l)]
    return pd.DataFrame(rows, columns=header)
