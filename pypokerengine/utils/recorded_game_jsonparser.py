import json


class Pot:
    def __init__(self, stage, num_players, size):
        self.stage = stage
        self.num_players = num_players
        self.size = size


class Bet:
    def __init__(self, actions):
        self.actions = actions

    def __iter__(self):
        return iter(self.actions.items())


class Player:
    def __init__(
        self, name, total_bet, bankroll, bets, pocket_cards, position, total_win
    ):
        self.name = name
        self.total_bet = total_bet
        self.bankroll = bankroll
        self.bets = bets
        self.pocket_cards = pocket_cards
        self.position = position
        self.total_win = total_win


def parse_json(data):
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        # Handle JSON parsing error
        print(f"Error parsing JSON: {e}")
        return None  # Or return some default value

    # Parse pots
    pots = []
    try:
        for pot in parsed_data["pots"]:
            pots.append(Pot(pot["stage"], pot["num_players"], pot["size"]))
    except (KeyError, TypeError) as e:
        # Handle errors accessing keys or invalid data types
        print(f"Error parsing pots: {e}")

    # Parse players and their pocket cards
    players = {}
    pocket_cards_map = {}
    try:
        for player_name, player_data in parsed_data["players"].items():
            bets = {}
            for bet in player_data["bets"]:
                stage = bet["stage"]
                actions = bet["actions"]
                bets[stage] = Bet(actions)
            players[player_name] = Player(
                player_name,
                player_data["total_bet"],
                player_data["bankroll"],
                bets,
                player_data["pocket_cards"],
                player_data["position"],
                player_data["total_win"],
            )
            # Create the pocket_cards_map with reversed and capitalized strings
            pocket_cards_map[player_name] = [
                card[1].upper() + card[0].upper()
                for card in player_data["pocket_cards"]
            ]
    except (KeyError, TypeError) as e:
        # Handle errors accessing keys or invalid data types
        print(f"Error parsing players: {e}")

    # Sort players by position
    sorted_players = dict(sorted(players.items(), key=lambda x: x[1].position))

    # Other attributes
    _id = parsed_data.get("_id")  # Use get() to avoid potential KeyError
    board = parsed_data.get("board")
    dealer = parsed_data.get("dealer")
    game = parsed_data.get("game")
    hand_num = parsed_data.get("hand_num")
    num_players = parsed_data.get("num_players")

    return (
        _id,
        board,
        dealer,
        game,
        hand_num,
        num_players,
        pots,
        sorted_players,
        pocket_cards_map,
    )


# Example usage:
json_data = """
{
    "_id": "holdem_199601_820830094",
    "board": ["Qc", "4s", "6s", "5d", "4d"],
    "dealer": 20,
    "game": "holdem",
    "hand_num": 1163,
    "num_players": 2,
    "pots": [
        {"stage": "f", "num_players": 2, "size": 20},
        {"stage": "t", "num_players": 2, "size": 60},
        {"stage": "r", "num_players": 2, "size": 100},
        {"stage": "s", "num_players": 2, "size": 100}
    ],
    "players": {
        "num": {
            "total_bet": 40,
            "bankroll": 1420,
            "bets": [
                {"actions": {"B": 10, "k": 0}, "stage": "p"},
                {"actions": {"b": 20}, "stage": "f"},
                {"actions": {"b": 20}, "stage": "t"},
                {"actions": {"k": 0}, "stage": "r"}
            ],
            "pocket_cards": ["9h", "Kh"],
            "position": 2,
            "total_win": 0
        },    
        "Jak": {
            "total_bet": 40,
            "bankroll": 850,
            "bets": [
                {"actions": {"B": 5, "c": 10}, "stage": "p"},
                {"actions": {"k": 0, "c": 20}, "stage": "f"},
                {"actions": {"k": 0, "c": 20}, "stage": "t"},
                {"actions": {"k": 0}, "stage": "r"}
            ],
            "pocket_cards": ["7c", "Ac"],
            "position": 1,
            "total_win": 80
        }
    }
}
"""

# _id, board, dealer, game, hand_num, num_players, pots, sorted_players, pocket_cards_map = parse_json(json_data)

# print("Sorted players:")
# for player_name, player in sorted_players.items():
#     print(f"Name: {player_name}, Bets at stage 't':")
#     for action, amount in player.bets.get('t', {}).actions.items():
#         print(f"  Action: {action}, Amount: {amount}")
#     x = player.bets.get('t', {}).actions.items()
#     print(list(x)[0][1])
# print("Pocket cards map:")
# for player_name, pocket_cards in pocket_cards_map.items():
#     print(f"{player_name}: {pocket_cards}")

# print(f"board cards: {board}")
