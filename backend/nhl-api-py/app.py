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
                fname = str(each['firstName']['default'])
                lname = str(each['lastName']['default'])
                height = str(each['heightInInches'] // 12) + "'" + str(each['heightInInches'] % 12) + '"'
                weight = each['weightInPounds']
                birthcountry = str(each['birthCountry'])
                birthcity = str(each['birthCity']['default'])
                birthdate = str(each['birthDate'])
                shootinghand = str(each['shootsCatches'])
                if each.get('birthStateProvince'):
                    birthstateprov = str(each['birthStateProvince']['default'])
                else:
                    birthstateprov = None
                playerdict = {
                    'id': each['id'],
                    'name': fname + ' ' + lname,
                    'height': height,
                    'weight': weight,
                    'birthCountry': birthcountry,
                    'birthStateOrProv': birthstateprov,
                    'birthCity' : birthcity,
                    'headshot': str(each['headshot']),
                    'sweaterNumber': each['sweaterNumber'],
                    'position': str(each['positionCode']),
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
        return jsonify({'error': 'Game is already over'}), 400

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

    # Wrong guess — advance stage or trigger final guess
    next_stage = game['stage'] + 1

    if next_stage >= len(CLUE_ORDER):
        # All clues revealed, this is the final guess
        if game['final_guess']:
            # They already had their final guess, game over
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