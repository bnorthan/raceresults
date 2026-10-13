from dateutil.parser import parse
import datetime
import re
import unicodedata
import pandas as pd

def time_to_hh_mm_ss_str(time):
    ts=time.split(':')
    if int(ts[0])>10:
        strtime='00:'+ts[0]+':'+ts[1]
    else:
        strtime=ts[0]+':'+ts[1]+':'+ts[2]
    return strtime

def parse_gender(gender_string):
    if str(gender_string).lower()[0]=='f':
        return 'F'
    else:
        return 'M'

def calculate_age(birthDate): 
    today = datetime.datetime.today() 
    age = today.year - birthDate.year - \
         ((today.month, today.day) < \
         (birthDate.month, birthDate.day)) 
  
    return age

def datestring_to_age(datestring):
    today=datetime.datetime.today()
    
    try: 
        dob=parse(datestring)
    except:
        dob=today
    
    return calculate_age(dob)

def date_to_age(dates):
    num_total=0
    num_errors=0
    
    for dateString in dates:
        print(dateString)
        num_total=num_total+1
        try: 
            date=parse(dateString)
        except:
            date=datetime.datetime.today
            num_errors=num_errors+1

    print("Num Total: "+str(num_total))
    print("Num Erros: "+str(num_errors))
 
def time_to_seconds(time):
    temp=time.split('.') 
    temp=temp[0].split(':')
    try:
        if (len(temp)==3):
            return 3600*int(temp[0])+60*int(temp[1])+int(temp[2])
        elif (len(temp)==2):
            return 60*int(temp[0])+int(temp[1])
        elif (len(temp)==1):
            return 60*int(temp[0])
    except:
        return -1
    
def strip_leading_zeros(time):
    return time.lstrip('0').lstrip(':')

def get_last_name(full_name):
    split=full_name.split()
    if len(split)>1:
        last_name=split[1];
    
        for i in range(2,len(split)):
            last_name=last_name+' '+split[i]
    else:
        last_name=''    
    return last_name


def fix_mojibake(text):
    """Undo utf-8 bytes that were decoded as a single-byte codec (possibly twice).

    Fixed-width result files are byte-aligned, so they must be read with a
    single-byte codec to keep the columns lined up; that turns a real utf-8
    apostrophe into 'a<euro>(tm)'.  This walks that back.
    """
    if not isinstance(text, str):
        return text
    for _ in range(3):
        for codec in ('cp1252', 'latin-1'):
            try:
                fixed = text.encode(codec).decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if fixed != text:
                text = fixed
                break
        else:
            break
    return text


# ---------------------------------------------------------------------------
# Matching one runner across years
# ---------------------------------------------------------------------------

def birth_window(age, race_date):
    """(earliest, latest) birth date consistent with being `age` on `race_date`,
    or None when the age is unknown.

    Someone who is a on day d was born after d - (a+1) years and on or before
    d - a years.  Results belong to the same person only if their windows
    overlap, which covers a birthday falling between two race dates (same age
    two years running, or +2) with no special case.
    """
    if age is None or pd.isna(age):
        return None
    d = pd.Timestamp(race_date)
    latest = d - pd.DateOffset(years=int(age))
    earliest = d - pd.DateOffset(years=int(age) + 1) + pd.Timedelta(days=1)
    return earliest.date(), latest.date()


def windows_overlap(w1, w2, slack_years=1):
    """True if two birth windows overlap, or miss by no more than slack_years
    (typos, ages taken at registration).  An unknown window overlaps anything."""
    if w1 is None or w2 is None:
        return True
    slack = datetime.timedelta(days=round(365.25 * slack_years))
    return w1[0] <= w2[1] + slack and w2[0] <= w1[1] + slack


# each group folds to its first entry; short forms shared by men's and
# women's names (Chris, Pat, Alex) get their own group and gender separates them
_NICKNAME_GROUPS = [
    ['robert', 'rob', 'robbie', 'bob', 'bobby'],
    ['william', 'will', 'willie', 'bill', 'billy'],
    ['james', 'jim', 'jimmy'],
    ['michael', 'mike', 'mikey', 'mick'],
    ['david', 'dave', 'davey'],
    ['thomas', 'tom', 'tommy'],
    ['joseph', 'joe', 'joey'],
    ['richard', 'rich', 'richie', 'rick', 'ricky', 'dick'],
    ['daniel', 'dan', 'danny'],
    ['edward', 'ed', 'eddie'],
    ['charles', 'charlie', 'chuck'],
    ['steven', 'stephen', 'steve'],
    ['anthony', 'tony'],
    ['andrew', 'andy'],
    ['matthew', 'matt'],
    ['timothy', 'tim'],
    ['kenneth', 'ken', 'kenny'],
    ['gregory', 'greg'],
    ['jeffrey', 'jeff', 'geoffrey', 'geoff'],
    ['douglas', 'doug'],
    ['gerald', 'jerry', 'gerry'],
    ['lawrence', 'laurence', 'larry'],
    ['ronald', 'ron', 'ronnie'],
    ['donald', 'don', 'donnie'],
    ['raymond', 'ray'],
    ['frederick', 'fred', 'freddie'],
    ['peter', 'pete'],
    ['benjamin', 'ben'],
    ['nicholas', 'nick'],
    ['phillip', 'philip', 'phil'],
    ['john', 'johnny', 'jon'],
    ['chris', 'christopher', 'christine', 'christina'],
    ['pat', 'patrick', 'patricia', 'patti', 'patty'],
    ['alex', 'alexander', 'alexandra'],
    ['kathy', 'katherine', 'kathryn', 'kathleen', 'catherine', 'cathy', 'kate', 'katie'],
    ['elizabeth', 'liz', 'beth', 'betsy', 'betty'],
    ['margaret', 'peg', 'peggy', 'maggie', 'meg'],
    ['susan', 'sue', 'susie', 'suzy'],
    ['deborah', 'debra', 'deb', 'debbie'],
    ['jennifer', 'jen', 'jenn', 'jenny'],
    ['rebecca', 'becky', 'becca'],
    ['barbara', 'barb'],
    ['cynthia', 'cindy'],
    ['pamela', 'pam'],
    ['judith', 'judy'],
    ['victoria', 'vicky', 'vicki'],
    ['theresa', 'teresa', 'terri'],
    ['kimberly', 'kim'],
]
_NICKNAMES = {nick: group[0] for group in _NICKNAME_GROUPS for nick in group}

# given names that show up as the second word of a first name ('Mary Ellen',
# 'Dee Ann', 'John David'), so a parser can keep them out of the last name
GIVEN_NAMES = set(_NICKNAMES) | {
    'ann', 'anne', 'beth', 'ellen', 'lou', 'jo', 'jane', 'marie', 'dee', 'lee', 'kay',
    'lynn', 'jude', 'agnes', 'kari', 'eileen', 'mae', 'jean', 'rose', 'olga', 'guy'}

NAME_SUFFIXES = {'jr', 'sr', 'ii', 'iii', 'iv'}


def _name_tokens(text):
    """Lowercase ascii tokens; apostrophes, '?', periods and other marks vanish,
    so O'Brien, O’Brien and O?Brien all give 'obrien', and 'Betz+++' gives 'betz'."""
    if not isinstance(text, str):
        return []
    text = fix_mojibake(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^a-z0-9\s,\-]', '', text.lower())
    return [t for t in re.split(r'[\s,\-]+', text) if t]


def normalize_name(first, last):
    """Matching key for a name -> (given, last, suffix).

    given:  first real name with nicknames folded ('Bob' -> 'robert'); middle
            initials drop out ('Don F' -> 'don', 'R Jeffrey' -> 'jeffrey'); a
            bare initial stays ('T' -> 't').
    last:   spaces and punctuation squeezed out ('St. John' -> 'stjohn',
            'De Boer' -> 'deboer', 'Saint John' -> 'stjohn').
    suffix: 'jr', 'sr', 'ii', 'iii' or 'iv' from either name, else ''.
    """
    f, l = _name_tokens(first), _name_tokens(last)
    suffix = ''
    for tokens in (l, f):
        while tokens and tokens[-1] in NAME_SUFFIXES:
            suffix = tokens.pop()
    if l and l[0] == 'saint':
        l[0] = 'st'

    real = [t for t in f if len(t) > 1]
    given = real[0] if real else (f[0] if f else '')
    return _NICKNAMES.get(given, given), ''.join(l), suffix


def last_name_parts(last):
    """The separate surnames in a two-part last name, so a married name can
    match the maiden or married name alone: 'Bertasso-Hughes' -> ['bertasso',
    'hughes'].  Every part must be 4+ letters, which leaves out particles:
    'St. John' -> [], 'Van Garderen' -> []."""
    tokens = [t for t in _name_tokens(last) if t not in NAME_SUFFIXES]
    return tokens if len(tokens) > 1 and all(len(t) >= 4 for t in tokens) else []
