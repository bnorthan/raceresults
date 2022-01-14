import pandas as pd
from scoreware.race.utils import get_last_name

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



