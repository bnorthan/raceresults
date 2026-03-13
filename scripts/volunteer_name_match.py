import pandas as pd
import Levenshtein

xl_volunteers=pd.ExcelFile('../data/2022/Totals/volunteers.xls')

#outname='../data/2022/spreadsheets/volunteers_matched.csv'
xl_totals=pd.ExcelFile('../data/2022/Totals/Totals_2023.xls')
out_name='../data/2022/Totals/volunteers_match.csv'


df_t=xl_totals.parse()
df_v=xl_volunteers.parse('Sheet1')

print(df_t.head())
print(df_v.head())


def match_volunteer_names(totals, vpoints, category):
    
    i=0;
    
    for index, row_v in vpoints.iterrows():
        print(i, row_v.Name)

        totals[category]=totals[category].fillna("")
        for index, row_t in totals.iterrows():
            #print(row_t[category])
            #print(row_v.Name)
    
            test=Levenshtein.ratio(row_v.Name, row_t[category])
            if (test>.7 and test<1):
                print(row_v.Name, row_t[category])

                answer = input("Is this a match?")
                
                if answer == 'y':
                    vpoints.at[i, 'Name']= row_t[category]
        i=i+1    

    return vpoints

vpoints=match_volunteer_names(df_t, df_v, "Male open name")
vpoints=match_volunteer_names(df_t, df_v, "Male 30-39 name")
vpoints=match_volunteer_names(df_t, df_v, "Male 40-49 name")
vpoints=match_volunteer_names(df_t, df_v, "Male 50-59 name")
vpoints=match_volunteer_names(df_t, df_v, "Male 60-69 name")
vpoints=match_volunteer_names(df_t, df_v, "Male 70+ name")

vpoints=match_volunteer_names(df_t, df_v, "Female open name")
vpoints=match_volunteer_names(df_t, df_v, "Female 30-39 name")
vpoints=match_volunteer_names(df_t, df_v, "Female 40-49 name")
vpoints=match_volunteer_names(df_t, df_v, "Female 50-59 name")
vpoints=match_volunteer_names(df_t, df_v, "Female 60-69 name")
vpoints=match_volunteer_names(df_t, df_v, "Female 70+ name")

vpoints.to_csv(out_name)