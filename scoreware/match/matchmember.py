import pandas as pd

import sys
import imp

from scoreware.runner.matcher import matchRunner

def match(members, runners, accept_score, ask_score):

    i=0
    max_score=[]
    match_info=[]
    
    for index, row_runners in runners.iterrows():
        max_score.append(0)
        match_info.append([])
        
        for index, row_members in members.iterrows():
            
            first1=row_runners.first_name.lower()
            last1=row_runners.last_name.lower()
            city1=row_runners.city.lower()
            gender1=row_runners.gender.strip()
            age1=row_runners.age
            
            first2=row_members['First name'].lower()
            last2=row_members['Last name'].lower()
            city2=str(row_members.City).lower()
            gender2=row_members.gender
            age2=row_members.age

            score = matchRunner(first1, last1, gender1, age1, city1, first2, last2, gender2, age2, city2)
                                        
            if (score>max_score[i]):
                max_score[i]=score
                match_info[i]=[first1, last1, age1, city1, first2, last2, age2, city2]
        i=i+1

    for i in range(len(max_score)):
        print (max_score[i]," ",match_info[i])

        answer='n'

        if (max_score[i]>accept_score):
            if (max_score[i]<ask_score):
                
                print((match_info[i],max_score[i]))
                answer = input("Is this a match?")
            else:
                answer='y'
                
        print(answer)
        if (answer=='y'):
            print('answer is yes')
            runners.at[i,'member']='yes' 
            runners.at[i,'mfname']=match_info[i][4].capitalize()
            runners.at[i,'mlname']=match_info[i][5].capitalize()
        else:      
            print('answer is no')
            runners.at[i,'member']='no'
            runners.at[i,'mfname']='nomatch'
            runners.at[i,'mlname']='nomatch'
 


    
