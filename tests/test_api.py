"""
API Testing Script for football-data.org
Quick way to test individual API calls

"""

import requests
import json

FOOTBALL_DATA_API_KEY = "7b428478107f4bdb98af277f262c4350"
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
PREMIER_LEAGUE_CODE = "PL" # English Premier League

def test_api_call(endpoint, params=None, verbose = True):
    """
    Generic helper function to call the football-data API.

    endpoint: string like 'teams/57'
    params: dictionary of query parameters (e.g., {'status': 'SCHEDULED'})
    """
    headers = {'X-Auth-Token': FOOTBALL_DATA_API_KEY}
    url = f"{FOOTBALL_DATA_BASE_URL}/{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Params: {params}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nFull Response:")
        if verbose:
            print(json.dumps(data, indent=2))
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Helper: Premier League-only filter
# Purpose: /teams/{id}/matches may include PL + other competitions (e.g., CL).
# This system is Premier League only
def filter_premier_league_matches(matches):
    return [m for m in matches if m.get('competition', {}).get('code') == PREMIER_LEAGUE_CODE]    
    
# SLOT: team (required)
#
# Endpoint used: /v4/competitions/PL/teams
# Purpose: Resolve team name to team ID

def get_arsenal_id():
    teams_result = test_api_call(f'competitions/{PREMIER_LEAGUE_CODE}/teams', verbose=False)

    if teams_result and teams_result.get('teams'):
        arsenal = next((t for t in teams_result['teams'] if 'Arsenal' in t['name']), None)
        if arsenal:
            print(f"\nResolved team 'Arsenal' to ID: {arsenal['id']}")
            return arsenal['id']
    return None    

# SLOT: manager
#
# Endpoint used: /v4/teams/{id}
# Purpose: Returns detailed team info including coach field

def test_manager_slot(team_id):
    print("\n--- Testing SLOT: manager ---")

    result = test_api_call(f'teams/{team_id}', verbose=False)

    if result and result.get('coach'):
        print(f"Manager (coach name): {result['coach']['name']}")
    else:
        print("Manager not found in response.")


# SLOTS:
# - leaguePosition
# - numGamesPlayed
# - winLossRecord
#
# Endpoint used: /v4/competitions/PL/standings
# Purpose: Returns league table including position, games played,
# wins, draws, losses

def test_standings_slots(team_id):
    print("\n--- Testing SLOTS: leaguePosition, numGamesPlayed, winLossRecord ---")

    result = test_api_call(f'competitions/{PREMIER_LEAGUE_CODE}/standings', verbose = False)

    if result and result.get('standings'):
        for standing_type in result['standings']:
            if standing_type['type'] == 'TOTAL':
                table = standing_type['table']

                team_row = next(
                    (row for row in table if row['team']['id'] == team_id),
                    None
                )

                if team_row:
                    print(f"leaguePosition: {team_row['position']}")
                    print(f"numGamesPlayed: {team_row['playedGames']}")
                    print(f"winLossRecord: "
                          f"{team_row['won']}-{team_row['draw']}-{team_row['lost']}")
                else:
                    print("Team not found in standings.")

# SLOTS:
# - nextGameDate
# - nextOpponent
#
# Endpoint used: /v4/teams/{id}/matches?status=SCHEDULED
# Purpose: Returns upcoming matches

def test_next_match_slots(team_id):
    print("\n--- Testing SLOTS: nextGameDate, nextOpponent ---")

    result = test_api_call(
        f'teams/{team_id}/matches',
        {'status': 'SCHEDULED'},
        verbose = False
    )

    if result and result.get('matches'):
        # Premier League only (ignore CL etc.)
        pl_matches = filter_premier_league_matches(result['matches'])

        if not pl_matches:
            print("No scheduled Premier League matches found.")
            return

        # Sort by utcDate ascending to guarantee we pick the next match
        pl_matches = sorted(pl_matches, key=lambda m: m['utcDate'])
        match = pl_matches[0]

        print(f"nextGameDate: {match['utcDate']}")

        # Determine opponent
        if match['homeTeam']['id'] == team_id:
            opponent = match['awayTeam']['name']
        else:
            opponent = match['homeTeam']['name']

        print(f"nextOpponent: {opponent}")
    else:
        print("No scheduled matches found.")

# SLOTS:
# - lastOpponent
# - lastScore
#
# Endpoint used: /v4/teams/{id}/matches?status=FINISHED
# Purpose: Returns completed matches including full-time score

def test_last_match_slots(team_id):
    print("\n--- Testing SLOTS: lastOpponent, lastScore ---")

    result = test_api_call(
        f'teams/{team_id}/matches',
        {'status': 'FINISHED'},
        verbose = False
    )

    if result and result.get('matches'):
        # Premier League only (ignore CL etc.)
        pl_matches = filter_premier_league_matches(result['matches'])

        if not pl_matches:
            print("No finished Premier League matches found.")
            return

        # Sort matches by utcDate descending to guarantee most recent first
        pl_matches = sorted(
            pl_matches,
            key=lambda m: m['utcDate'],
            reverse=True
        )

        match = pl_matches[0]

        # Determine opponent
        if match['homeTeam']['id'] == team_id:
            opponent = match['awayTeam']['name']
        else:
            opponent = match['homeTeam']['name']

        full_time = match['score']['fullTime']

        print(f"lastOpponent: {opponent}")
        print(f"lastScore: {full_time['home']} - {full_time['away']}")
    else:
        print("No finished matches found.")


# SLOT: playingNow
#
# Endpoint used: /v4/teams/{id}/matches?status=IN_PLAY
# Purpose: Checks if team currently has a live match

def test_playing_now_slot(team_id):
    print("\n--- Testing SLOT: playingNow ---")

    result = test_api_call(
        f'teams/{team_id}/matches',
        {'status': 'IN_PLAY'},
        verbose = False
    )

    if result and result.get('matches'):
        # Premier League only (ignore CL etc.)
        pl_matches = filter_premier_league_matches(result['matches'])

        if len(pl_matches) > 0:
            print("playingNow: TRUE (team has a live Premier League match)")
        else:
            print("playingNow: FALSE (team not currently playing a Premier League match)")
    else:
        print("playingNow: FALSE (team not currently playing a Premier League match)")


# RUN ALL SLOT TESTS
def test_all():
    print("\n" + "="*60)
    print("RUNNING ALL API TESTS (football-data.org)")
    print("="*60)
    
    team_id = get_arsenal_id()

    if team_id:
        test_manager_slot(team_id)
        test_standings_slots(team_id)
        test_next_match_slots(team_id)
        test_last_match_slots(team_id)
        test_playing_now_slot(team_id)
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_all()
