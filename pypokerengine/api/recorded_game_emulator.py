from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.game_state_utils import (
    attach_hole_card,
    replace_community_card,
)
from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.utils.recorded_game_jsonparser import parse_json
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.engine.card import Card
from pypokerengine.engine.dealer import MessageSummarizer
from pypokerengine.api.emulator import Emulator
import uuid
from collections import OrderedDict

message_summarizer = MessageSummarizer(verbose=2)
street_to_json_map = {"preflop": "p", "flop": "f", "turn": "t", "river": "r"}
json_actions_to_index_map = {"c": 1, "k": 1, "b": 2, "f": 0}


class RecordedPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"
    prev_call_amt = 0

    def __init__(self, player_name, playerobj):
        super().__init__()
        self.player_name = player_name
        self.playerobj = playerobj
        self.json_streetiter_index_map = {
            "p": 1,  # since small and big blind actions are accounted for in RoundManger.startround()
            "f": 0,
            "t": 0,
            "r": 0,
        }

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        try:
            json_street = street_to_json_map[round_state["street"]]
        except KeyError as e:
            # Handle missing street key in round_state
            print(f"Error: Invalid street value in round_state: {e}")
            return None  # Or return some default value

        if json_street is None:
            # Handle case where street_to_json_map doesn't have a mapping for the value
            print(
                f"Warning: Street '{round_state['street']}' not found in street_to_json_map"
            )
            return None  # Or return some default value

        try:
            json_actions = list(
                self.playerobj.bets.get(json_street, {}).actions.items()
            )
        except (AttributeError, KeyError) as e:
            # Handle errors accessing playerobj.bets or missing key in bets
            print(f"Error getting player actions for street '{json_street}': {e}")
            return None  # Or return some default value

        try:
            index = self.json_streetiter_index_map[json_street]
            if index >= len(json_actions):
                raise IndexError("Index out of range")
        except (KeyError, IndexError) as e:
            # Handle missing index in json_streetiter_index_map or index out of bounds
            print(f"Error accessing actions for street '{json_street}': {e}")
            return None  # Or return some default value

        self.json_streetiter_index_map[
            json_street
        ] += 1  # increment the index to access next actions for the same street

        try:
            json_action = json_actions[index][0]
            call_action_info = valid_actions[json_actions_to_index_map[json_action]]
            amount = json_actions[index][1]
        except IndexError as e:
            # Handle potential IndexError if list is empty after incrementing index
            print(f"Error retrieving action and amount for street '{json_street}': {e}")
            return None  # Or return some default value

        # As check is not defined in PyPokerEngine, hence simulating checks with calls
        # TODO: verify if check is same as call with previous called amount.
        # Or it would be 0 for streets flop onwards and call with prev_call_amt for preflop street?
        # TODO: compare against some defined constants instead of literals
        # Assuming for now that below logic holds true only for preflop
        if json_street == "p":
            if json_action == "c":
                RecordedPlayer.prev_call_amt = amount
            elif json_action == "k":
                amount = RecordedPlayer.prev_call_amt
        return call_action_info["action"], amount  # return action and amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass  # action returned here is sent to the poker engine

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


comm_cards_placed = {
    Const.Street.FLOP: False,
    Const.Street.TURN: False,
    Const.Street.RIVER: False,
}
to_card = lambda s: Card.from_str(s)


def run_recorded_round_until_finish(emu, game_state, board):
    mailbox = []
    while game_state["street"] != Const.Street.FINISHED:

        # Handle flop card placement
        if (
            game_state["street"] == Const.Street.FLOP
            and not comm_cards_placed[Const.Street.FLOP]
        ):
            try:
                flop_cards = [card[1].upper() + card[0].upper() for card in board[:3]]
                cards = [to_card(c) for c in flop_cards]
                game_state = replace_community_card(game_state, cards)
                comm_cards_placed[Const.Street.FLOP] = True
            except (IndexError, TypeError) as e:
                print(f"Error processing flop cards: {e}")
                # Handle error (e.g., log error, skip flop processing)

        # Handle turn card placement (similar logic)
        elif (
            game_state["street"] == Const.Street.TURN
            and not comm_cards_placed[Const.Street.TURN]
        ):
            try:
                turn_cards = [card[1].upper() + card[0].upper() for card in board[:4]]
                cards = [to_card(c) for c in turn_cards]
                game_state = replace_community_card(game_state, cards)
                comm_cards_placed[Const.Street.TURN] = True
            except (IndexError, TypeError) as e:
                print(f"Error processing turn card: {e}")
                # Handle error (e.g., log error, skip turn processing)

        # Handle river card placement (similar logic)
        elif (
            game_state["street"] == Const.Street.RIVER
            and not comm_cards_placed[Const.Street.RIVER]
        ):
            try:
                river_cards = [card[1].upper() + card[0].upper() for card in board]
                cards = [to_card(c) for c in river_cards]
                game_state = replace_community_card(game_state, cards)
                comm_cards_placed[Const.Street.RIVER] = True
            except (IndexError, TypeError) as e:
                print(f"Error processing river card: {e}")
                # Handle error (e.g., log error, skip river processing)

        # Player related operations
        try:
            next_player_pos = game_state["next_player"]
            next_player_uuid = game_state["table"].seats.players[next_player_pos].uuid
            next_player_algorithm = emu.fetch_player(next_player_uuid)

            msg = MessageBuilder.build_ask_message(next_player_pos, game_state)[
                "message"
            ]
            action, amount = next_player_algorithm.declare_action(
                msg["valid_actions"], msg["hole_card"], msg["round_state"]
            )

            game_state, messages = RoundManager.apply_action(game_state, action, amount)
            message_summarizer.summarize_messages(messages)
            mailbox += messages

        except (KeyError, AttributeError) as e:
            print(f"Error retrieving player information or action: {e}")
            # Handle error (e.g., log error, skip player action)

        # Handle message processing
        events = [emu.create_event(message[1]["message"]) for message in mailbox]
        events = [e for e in events if e]

    if emu._is_last_round(game_state, emu.game_rule):
        events += emu._generate_game_result_event(game_state)
    return game_state, events


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


def replay_game(json_data):
    """Processes a poker game based on provided JSON data.

    Args:
        json_data (str): JSON string representing the recorded game data.

    Returns:
        dict: Dictionary containing game state and events.
    """
    try:
        # Parse JSON data
        (
            _id,
            board,
            dealer,
            game,
            hand_num,
            num_players,
            pots,
            sorted_players,
            pocket_cards_map,
        ) = parse_json(json_data)
    except Exception as e:
        print(f"Error parsing JSON data: {e}")
        return None  # Or handle error differently

    # Emulator setup
    emu = Emulator()
    try:
        emu.set_game_rule(
            player_num=num_players, max_round=1, small_blind_amount=5, ante_amount=0
        )
    except (TypeError, ValueError) as e:
        print(f"Error setting game rule: {e}")
        return None  # Or handle error differently

    players_info = OrderedDict()
    playername_uuidmap = {}
    for player_name, player in sorted_players.items():
        try:
            p = RecordedPlayer(player_name, player)
            # Generate a random UUID
            random_uuid = uuid.uuid4()
            player_uuid_str = str(random_uuid)
            emu.register_player(player_uuid_str, p)
            playername_uuidmap[player_name] = player_uuid_str
            player_info = {"name": player_name, "stack": player.bankroll}
            players_info[player_uuid_str] = player_info
            players_info.move_to_end(
                player_uuid_str, last=False
            )  # Descending order of position
        except (KeyError, AttributeError) as e:
            print(f"Error processing player '{player_name}': {e}")
            # Handle error (e.g., skip player, log error)

    # Initial game state
    try:
        initial_game_state = emu.generate_initial_game_state(players_info)
    except Exception as e:
        print(f"Error generating initial game state: {e}")
        return None  # Or handle error differently

    # Start new round
    try:
        game_state, events = emu.start_new_round(initial_game_state, message_summarizer)
    except Exception as e:
        print(f"Error starting new round: {e}")
        return None  # Or handle error differently

    # Attach hole cards
    for player in game_state["table"].seats.players:
        try:
            game_state = attach_hole_card(
                game_state,
                playername_uuidmap[player.name],
                gen_cards(pocket_cards_map[player.name]),
            )
        except (KeyError, ValueError) as e:
            print(f"Error attaching hole card for player '{player.name}': {e}")
            # Handle error (e.g., skip player, log error)

    # Run round
    try:
        game_state, final_event = run_recorded_round_until_finish(
            emu, game_state, board
        )
    except Exception as e:
        print(f"Error running recorded round: {e}")
        return None  # Or handle error differently

    # Return game state and events
    return {"game_state": game_state, "events": events}


# Example usage (direct execution)
if __name__ == "__main__":
    #   with open("game_data.json", "r") as f:  # Replace with your JSON loading logic
    #     json_data = f.read()
    result = replay_game(json_data)
    if result:
        print(result)  # Print the game state and events
