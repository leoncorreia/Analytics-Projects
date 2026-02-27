import requests
from ratelimit import limits, sleep_and_retry
from langchain.tools import tool

FPL_DATA = None

# --- RATE LIMITER SETUP ---
# Limit to 1 call per 1 second to prevent getting blocked by FPL servers.
@sleep_and_retry
@limits(calls=1, period=1)
def fetch_fpl_api(url: str):
    """All FPL API requests must pass through this rate-limited function."""
    headers = {"User-Agent": "FPL-AI-Agent/1.0"}
    return requests.get(url, headers=headers)
# --------------------------

def get_fpl_data():
    """Caches the massive main FPL dataset in memory."""
    global FPL_DATA
    if FPL_DATA is None:
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        FPL_DATA = fetch_fpl_api(url).json()
    return FPL_DATA

def get_current_gameweek():
    """Helper function to find the current Gameweek number."""
    data = get_fpl_data()
    for event in data['events']:
        if event['is_current']:
            return event['id']
    return 1 # Fallback to 1 if the season hasn't started yet

@tool
def get_player_stats(player_name: str) -> str:
    """Gets current FPL stats (price, points, form, team) for a specific player."""
    data = get_fpl_data()
    for player in data['elements']:
        if player_name.lower() in player['web_name'].lower() or \
           player_name.lower() in player['first_name'].lower() or \
           player_name.lower() in player['second_name'].lower():
            
            team_id = player['team']
            team_name = next((t['name'] for t in data['teams'] if t['id'] == team_id), "Unknown")
            price = player['now_cost'] / 10 
            
            return f"Player: {player['first_name']} {player['second_name']} ({team_name}) | Price: £{price}m | Form: {player['form']} | Total Points: {player['total_points']}"
            
    return f"Could not find a player matching '{player_name}'. Check spelling."

@tool
def get_team_fixtures(team_name: str) -> str:
    """Gets the next 3 upcoming Premier League fixtures and Fixture Difficulty Rating (FDR) for a team."""
    data = get_fpl_data()
    team_id = None
    actual_team_name = ""
    
    for team in data['teams']:
        if team_name.lower() in team['name'].lower():
            team_id = team['id']
            actual_team_name = team['name']
            break
            
    if not team_id:
        return f"Team '{team_name}' not found."
        
    fixtures_url = "https://fantasy.premierleague.com/api/fixtures/?future=1"
    # Using the rate-limited function here
    fixtures = fetch_fpl_api(fixtures_url).json()
    
    upcoming = []
    for f in fixtures:
        if f['team_a'] == team_id or f['team_h'] == team_id:
            is_home = f['team_h'] == team_id
            opponent_id = f['team_a'] if is_home else f['team_h']
            
            opponent_name = next((t['name'] for t in data['teams'] if t['id'] == opponent_id), "Unknown")
            fdr = f['team_h_difficulty'] if is_home else f['team_a_difficulty']
            venue = "Home" if is_home else "Away"
            
            upcoming.append(f"vs {opponent_name} ({venue}) - FDR: {fdr}")
            if len(upcoming) >= 3:
                break
                
    return f"Upcoming 3 fixtures for {actual_team_name}:\n" + "\n".join(upcoming)

@tool
def check_player_availability(player_name: str) -> str:
    """Checks if a player is injured, suspended, or flagged, and gives their return date/status."""
    data = get_fpl_data()
    for player in data['elements']:
        if player_name.lower() in player['web_name'].lower() or \
           player_name.lower() in player['second_name'].lower():
            
            status = player['status']
            news = player['news']
            chance_next_round = player['chance_of_playing_next_round']
            
            if status == 'a':
                return f"{player['web_name']} is currently 100% fit and available."
            elif status == 'd':
                return f"WARNING: {player['web_name']} is flagged (Doubtful). Chance of playing: {chance_next_round}%. News: {news}"
            elif status == 'i':
                return f"WARNING: {player['web_name']} is INJURED. News: {news}"
            elif status == 's':
                return f"WARNING: {player['web_name']} is SUSPENDED. News: {news}"
            elif status == 'n':
                return f"WARNING: {player['web_name']} is UNAVAILABLE. News: {news}"
                
    return f"Could not find injury data for '{player_name}'."

@tool
def get_my_team(manager_id: int) -> str:
    """Fetches the current 15-man squad for a specific FPL Manager ID."""
    gw = get_current_gameweek()
    url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gw}/picks/"
    
    # Using the rate-limited function here
    response = fetch_fpl_api(url)
    
    if response.status_code != 200:
        return f"Could not find team for Manager ID {manager_id}. Make sure the ID is correct."
        
    picks_data = response.json()
    main_data = get_fpl_data()
    
    team_list = []
    for pick in picks_data['picks']:
        player_id = pick['element']
        is_captain = pick['is_captain']
        is_vice = pick['is_vice_captain']
        
        player_name = next((p['web_name'] for p in main_data['elements'] if p['id'] == player_id), "Unknown")
        
        role = ""
        if is_captain: role = " (Captain)"
        elif is_vice: role = " (Vice-Captain)"
        
        team_list.append(f"- {player_name}{role}")
        
    return f"Here is the manager's current team for Gameweek {gw}:\n" + "\n".join(team_list)