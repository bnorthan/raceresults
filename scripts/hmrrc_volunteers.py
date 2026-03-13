import pandas as pd
import operator
from difflib import SequenceMatcher

def merge_vpoints(totals, vpoints, category):
    left_cname=category+' name'
    left_cscore=category+' score'
    right_cname='Name'
    temp=totals[[left_cname, left_cscore]]
    merged=temp.merge(vpoints, left_on=left_cname, right_on=right_cname, how='left')
    merged=merged.drop('Name',axis=1)
    merged['volunteer']=merged['volunteer'].fillna(0)
    merged['total']=merged[left_cscore]+merged['volunteer']
    return merged 

xl_totals=pd.ExcelFile('../data/2022/Totals/Totals_2023.xls')
out_name='../data/2022/Totals/total_with_volunteer.csv'


who='Male'

#df_v=xl_volunteers.parse('Sheet1')
df_v=pd.read_csv('../data/2022/Totals/volunteers_match.csv')
print(df_v.head())

df_totals=xl_totals.parse();
print(df_totals.head())

test=df_totals[["Male open score", "Male open name"]]
test2=test.merge(df_v, left_on='Male open name', right_on='Name')

#test=df_totals[["Male 30-39 score", "Male 30-39 name"]]
#test2=test.merge(df_v, left_on='Male 30-39 name', right_on='Name', how='left')
m_open_merge=  merge_vpoints(df_totals, df_v,"Male open")
m_30_39_merge = merge_vpoints(df_totals, df_v,"Male 30-39")
m_40_49_merge = merge_vpoints(df_totals, df_v,"Male 40-49")
m_50_59_merge = merge_vpoints(df_totals, df_v,"Male 50-59")
m_60_69_merge = merge_vpoints(df_totals, df_v,"Male 60-69")
m_70p_merge = merge_vpoints(df_totals, df_v,"Male 70+")

males=pd.concat([m_open_merge, m_30_39_merge, m_40_49_merge, m_50_59_merge, m_60_69_merge, m_70p_merge], axis=1)

f_open_merge=  merge_vpoints(df_totals, df_v,"Female open")
f_30_39_merge = merge_vpoints(df_totals, df_v,"Female 30-39")
f_40_49_merge = merge_vpoints(df_totals, df_v,"Female 40-49")
f_50_59_merge = merge_vpoints(df_totals, df_v,"Female 50-59")
f_60_69_merge = merge_vpoints(df_totals, df_v,"Female 60-69")
f_70p_merge = merge_vpoints(df_totals, df_v,"Female 70+")

females=pd.concat([f_open_merge, f_30_39_merge, f_40_49_merge, f_50_59_merge, f_60_69_merge, f_70p_merge], axis=1)

totals=pd.concat([males, females],axis=1)

totals.to_csv(out_name)