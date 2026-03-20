from nhlpy import NHLClient
import pandas as pd

# Basic usage
client = NHLClient()

# Get all teams
teams = client.teams.teams()
# print(teams)
teamslist = []
for team in teams:
  teamabbr = str(team['abbr'])
  teamslist.append(teamabbr)
print(teamslist)

# # Get current standings
# standings = client.standings.league_standings()

# # Get today's games
# games = client.schedule.daily_schedule()
# team = 'SJS'
df = pd.DataFrame()
for team in teamslist : 
  roster = client.teams.team_roster(team_abbr=team, season="20252026")
  # print(f"Forwards: {len(roster['forwards'])}")
  # print(f"Defensemen: {len(roster['defensemen'])}")
  # print(f"Goalies: {len(roster['goalies'])}")
  # print(roster['forwards'])
  positiontypes = ['forwards', 'defensemen', 'goalies']
  for position in positiontypes : 
    teambyposition = []
    for each in roster[position]:
      fname = str(each['firstName']['default'])
      lname = str(each['lastName']['default'])
      height = str(each['heightInInches']//12) + "'" + str(each['heightInInches'] % 12) + '"'
      weight = each['weightInPounds']
      birthcity = str(each['birthCity']['default'])
      birthcountry = str(each['birthCountry'])
      if each.get('birthStateProvince'):
        birthstateprov = str(each['birthStateProvince']['default'])
      else:
        birthstateprov = None
      id = each['id']
      headshot = str(each['headshot'])
      number = each['sweaterNumber']
      position = str(each['positionCode'])
      shootinghand = str(each['shootsCatches'])
      birthdate = str(each['birthDate'])
      fullname = fname + ' ' + lname
      playerdict = {'id': id, 'name' : fullname, 'height' : height, 'weight': weight, 
                    'birthCity' : birthcity, 'birthStateOrProv' : birthstateprov, 'birthCountry' : birthcountry, 'birthDate' : birthdate,
                    'headshot' : headshot, 'sweaterNumber' : number, 'position' : position, 'shootingHand' : shootinghand, 'teamAbbr' : team
                    }

      teambyposition.append(playerdict)


    teamposdf = pd.DataFrame(teambyposition)
    df = pd.concat([df, teamposdf], ignore_index=True)
    
print(df.head())
print(df.shape)