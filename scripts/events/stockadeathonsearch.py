from raceresults.models import Result
from raceresults.models import Race

test=Result.objects.filter(last_name__iexact='Mindel')

for race in Race.objects.filter(id=2):
    print(race.id)


for r in test:
    race=Race.objects.filter(id=r.race_id)
    print(r.first_name, r.last_name, r.time, race[0].race_date)
  