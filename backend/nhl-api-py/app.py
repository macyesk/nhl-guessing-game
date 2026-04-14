from nhlpy import NHLClient
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
import random

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
client = NHLClient()

# --- Build roster df on startup ---
def build_roster_df():
    teams = client.teams.teams()
    teamslist = [str(team['abbr']) for team in teams]
    df = pd.DataFrame()
    for team in teamslist:
        roster = client.teams.team_roster(team_abbr=team, season="20252026")
        for positiontype in ['forwards', 'defensemen', 'goalies']:
            teambyposition = []
            for each in roster[positiontype]:
                # Safely extract firstName
                fname = each.get('firstName')
                fname = fname.get('default') if fname else None
                fname = str(fname) if fname else None
                
                # Safely extract lastName
                lname = each.get('lastName')
                lname = lname.get('default') if lname else None
                lname = str(lname) if lname else None
                
                # Safely extract and format height
                height_inches = each.get('heightInInches')
                if height_inches:
                    height = str(height_inches // 12) + "'" + str(height_inches % 12) + '"'
                else:
                    height = None
                
                # Safely extract weight
                weight = each.get('weightInPounds')
                
                # Safely extract birthCountry
                birthcountry = each.get('birthCountry')
                birthcountry = str(birthcountry) if birthcountry else None
                
                # Safely extract birthCity
                birthcity = each.get('birthCity')
                birthcity = birthcity.get('default') if birthcity else None
                birthcity = str(birthcity) if birthcity else None
                
                # Safely extract birthDate
                birthdate = each.get('birthDate')
                birthdate = str(birthdate) if birthdate else None
                
                # Safely extract shootingHand
                shootinghand = each.get('shootsCatches')
                shootinghand = str(shootinghand) if shootinghand else None
                
                # Safely extract birthStateProvince
                birthstateprov = each.get('birthStateProvince')
                birthstateprov = birthstateprov.get('default') if birthstateprov else None
                birthstateprov = str(birthstateprov) if birthstateprov else None
                
                # Safely extract sweater number
                sweater_number = each.get('sweaterNumber')
                
                # Safely extract headshot
                headshot = each.get('headshot')
                headshot = str(headshot) if headshot else None
                
                # Safely extract positionCode
                position = each.get('positionCode')
                position = str(position) if position else None
                
                # Build player dict with safe values
                full_name = None
                if fname and lname:
                    full_name = fname + ' ' + lname
                elif fname:
                    full_name = fname
                elif lname:
                    full_name = lname
                
                playerdict = {
                    'id': each.get('id'),
                    'name': full_name,
                    'height': height,
                    'weight': weight,
                    'birthCountry': birthcountry,
                    'birthStateOrProv': birthstateprov,
                    'birthCity' : birthcity,
                    'headshot': headshot,
                    'sweaterNumber': sweater_number,
                    'position': position,
                    'teamAbbr': team,
                    'birthDate' : birthdate,
                    'shootingHand' : shootinghand
                }
                teambyposition.append(playerdict)
            teamposdf = pd.DataFrame(teambyposition)
            df = pd.concat([df, teamposdf], ignore_index=True)
    return df

print("Building roster data...")
df = build_roster_df()
print(f"Loaded {len(df)} players.")

# --- In-memory game state ---
games = {}

CLUE_ORDER = ['birthCountry', 'birthStateOrProv','birthCity','birthDate', 'height', 'weight', 'sweaterNumber', 'position','shootingHand', 'teamAbbr', 'headshot']

def get_clues_up_to_stage(player, stage):
    clues = {}
    for i in range(min(stage + 1, len(CLUE_ORDER))):
        key = CLUE_ORDER[i]
        clues[key] = player[key]
    return clues

# --- Endpoints ---
@app.route('/game/new')
def new_game():
    player = df.sample(1).iloc[0].to_dict()
    game_id = str(uuid.uuid4())
    games[game_id] = {
        'player': player,
        'stage': 0,        # which clue we're on (0 = first clue revealed)
        'final_guess': False,
        'over': False
    }
    return jsonify({
        'game_id': game_id,
        'clues': get_clues_up_to_stage(player, 0)
    })

@app.route('/game/<game_id>/guess', methods=['POST'])
def make_guess(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404

    game = games[game_id]

    if game['over']:
        return jsonify({
            'correct': False,
            'game_over': True,
            'name': game['player']['name'],
            'clues': get_clues_up_to_stage(game['player'], len(CLUE_ORDER) - 1)
        })

    data = request.get_json()
    guess = data.get('guess', '').strip().lower()
    correct_name = game['player']['name'].lower()
    correct = guess == correct_name

    if correct:
        game['over'] = True
        return jsonify({
            'correct': True,
            'name': game['player']['name'],
            'clues': get_clues_up_to_stage(game['player'], len(CLUE_ORDER) - 1)
        })

    next_stage = game['stage'] + 1

    if next_stage >= len(CLUE_ORDER):
        if game['final_guess']:
            game['over'] = True
            return jsonify({
                'correct': False,
                'game_over': True,
                'name': game['player']['name'],
                'clues': get_clues_up_to_stage(game['player'], len(CLUE_ORDER) - 1)
            })
        else:
            game['final_guess'] = True
            return jsonify({
                'correct': False,
                'final_guess': True,
                'name': game['player']['name'],
                'clues': get_clues_up_to_stage(game['player'], len(CLUE_ORDER) - 1)
            })
    else:
        game['stage'] = next_stage
        return jsonify({
            'correct': False,
            'clues': get_clues_up_to_stage(game['player'], next_stage)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001)