import pandas as pd
import raceutil

def parse_general(df, headers, id):

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
                    newdf['last_name']=df[column].apply(lambda x: raceutil.getLastName(x))
                    print(newdf['last_name'])
                    
                else:
                    if (key=='age'):
                        df[column]=df[column].fillna(value=-1)
                    else:
                        df[column]=df[column].fillna(value='none')
                    newdf[key]=df[column]

    newdf['race_id']=id

    return newdf



