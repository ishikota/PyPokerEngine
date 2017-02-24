DIVIDER = "="*70

def visualize_game_start(game_info, uuid=None):
    ls = []
    ls.append(_visualize_title("Game start", uuid))
    ls.append(DIVIDER)
    ls.append(_visualize_sub_title("rule"))
    ls.append(_visualize_item("%d players game" % game_info["player_num"]))
    ls.append(_visualize_item("%d round" % game_info["rule"]["max_round"]))
    ls.append(_visualize_item("start stack = %s" % game_info["rule"]["initial_stack"]))
    ls.append(_visualize_item("       ante = %s" % game_info["rule"]["ante"]))
    ls.append(_visualize_item("small blind = %s" % game_info["rule"]["small_blind_amount"]))
    if len(game_info["rule"]["blind_structure"]) != 0:
        ls.append(_visualize_item("blind structure"))
        for round_count in game_info["rule"]["blind_structure"]:
            level_info = game_info["rule"]["blind_structure"][round_count]
            ante, sb_amount = level_info["ante"], level_info["small_blind"]
            ls.append(_visualize_sub_item("after %d round : ante = %s, sb_amount = %s" %(
                round_count, ante, sb_amount)))
    ls.append(DIVIDER)
    return "\n".join(ls)

def visualize_round_start(round_count, hole_card, seats, uuid=None):
    ls = []
    ls.append(_visualize_title("Round %d start" % round_count, uuid))
    ls.append(DIVIDER)
    ls.append(_visualize_sub_title("hole card"))
    ls.append(_visualize_item(str(hole_card)))
    ls.append(_visualize_sub_title("players information"))
    for idx, player_info in enumerate(seats):
        player_str = "%d : %s" % (idx, visualize_player(player_info))
        ls.append(_visualize_item(player_str))
    ls.append(DIVIDER)
    return "\n".join(ls)

def visualize_street_start(street, _round_state, uuid=None):
    ls = []
    ls.append(_visualize_title("New street start", uuid))
    ls.append(DIVIDER)
    ls.append(_visualize_sub_title("street"))
    ls.append(_visualize_item(street))
    ls.append(DIVIDER)
    return "\n".join(ls)

def visualize_declare_action(valid_actions, hole_card, round_state, uuid=None):
    ls = []
    ls.append(_visualize_title("Declare your action", uuid))
    ls.append(DIVIDER)
    ls.append(_visualize_sub_title("valid actions"))
    ls.append(_visualize_item(valid_actions[0]["action"]))
    ls.append(_visualize_item("%s: %s" % (valid_actions[1]["action"], valid_actions[1]["amount"])))
    ls.append(_visualize_item("%s: %s" % (
        valid_actions[2]["action"],
        [valid_actions[2]["amount"]["min"], valid_actions[2]["amount"]["max"]])
    ))
    ls.append(_visualize_sub_title("hole card"))
    ls.append(_visualize_item(str(hole_card)))
    ls.append(_visualize_sub_title("round state"))
    ls.append(visualize_round_state(round_state))
    ls.append(DIVIDER)
    return "\n".join(ls)

def visualize_game_update(new_action, round_state, uuid=None):
    ls = []
    ls.append(_visualize_title("Game update", uuid))
    ls.append(DIVIDER)
    ls.append(_visualize_sub_title("new action"))
    ls.append(_visualize_item("%s (%s) declared %s" % (
        _fetch_player_name(new_action["player_uuid"], round_state),
        new_action["player_uuid"],
        "%s: %s" % (new_action["action"], new_action["amount"])
    )))
    ls.append(_visualize_sub_title("round state"))
    ls.append(visualize_round_state(round_state))
    ls.append(DIVIDER)
    return "\n".join(ls)

def _fetch_player_name(uuid, rs):
    if uuid not in [p["uuid"] for p in rs["seats"]]:
        raise Exception("player of uuid = [ %s ] not found in round state => %s" %(uuid, rs))
    return [p["name"] for p in rs["seats"] if p["uuid"]==uuid][0]

def visualize_round_result(winners, hand_info, round_state, uuid=None):
    ls = []
    ls.append(_visualize_title("Round result", uuid))
    ls.append(DIVIDER)
    ls.append(_visualize_sub_title("winners"))
    for winner in winners:
        ls.append(_visualize_item(visualize_player(winner)))
    if len(hand_info) != 0:
        ls.append(_visualize_sub_title("hand info"))
        for info in hand_info:
            ls.append(visualize_hand_info(info, round_state))
    ls.append(_visualize_sub_title("round state"))
    ls.append(visualize_round_state(round_state))
    ls.append(DIVIDER)
    return "\n".join(ls)

def visualize_hand_info(info, round_state):
    ls = []
    uuid = info["uuid"]
    name = _fetch_player_name(uuid, round_state)
    hand, hole = info["hand"]["hand"], info["hand"]["hole"]
    ls.append(_visualize_item("%s (%s)" % (name, uuid)))
    ls.append(_visualize_sub_item("hand => %s (high=%d, low=%d)" % (
        hand["strength"], hand["high"], hand["low"])))
    ls.append(_visualize_sub_item("hole => [%s, %s]" % (hole["high"], hole["low"])))
    return "\n".join(ls)

def visualize_player(player):
    return "%s (%s) => state : %s, stack : %s" % (
            player["name"], player["uuid"], player["state"], player["stack"])

def visualize_round_state(rs):
    ls = []
    ls.append(_visualize_item("dealer btn : %s" % rs["seats"][rs["dealer_btn"]]["name"]))
    ls.append(_visualize_item("street : %s" % rs["street"]))
    ls.append(_visualize_item("community card : %s" % rs["community_card"]))
    ls.append(_visualize_item("pot : main = %s, side = %s" % (
        rs["pot"]["main"]["amount"], rs["pot"]["side"])))
    ls.append(_visualize_item("players information"))
    for idx, player_info in enumerate(rs["seats"]):
        player_str = visualize_player_with_badge(player_info, rs)
        player_str = player_str.replace("NEXT", "CURRENT")
        ls.append(_visualize_sub_item("%d : %s" % (idx, player_str)))
    ls.append(_visualize_item("action histories"))
    sort_key = lambda e: {"preflop":0, "flop":1, "turn":2, "river":3}[e[0]]
    for street, histories in sorted(rs["action_histories"].items(), key=sort_key):
        if len(histories) != 0:
            ls.append(_visualize_sub_item(street))
            for history in histories:
                summary = {k:v for k,v in history.items()}
                uuid = summary.pop("uuid")
                summary["player"] = "%s (uuid=%s)" % (_fetch_player_name(uuid, rs), uuid)
                ls.append(_visualize_sub_sub_item(str(summary)))
    return "\n".join(ls)

def visualize_player_with_badge(player, rs):
    p_pos = rs["seats"].index(player)
    is_sb = p_pos == rs["small_blind_pos"]
    is_bb = p_pos == rs["big_blind_pos"]
    is_next = _is_next_player(player, rs)
    player_str = visualize_player(player)
    player_str += _gen_badge(is_sb, is_bb, is_next)
    return player_str

def _is_next_player(player, rs):
    return rs and not isinstance(rs["next_player"], str)\
            and player == rs["seats"][rs["next_player"]]

def _gen_badge(is_sb, is_bb, is_next):
    badges = []
    if is_sb: badges.append("SB")
    if is_bb: badges.append("BB")
    if is_next: badges.append("NEXT")
    badge_str = ""
    if len(badges) != 0:
        badge_str = ", ".join(badges)
        badge_str = " <= %s" % badge_str
    return badge_str

def _visualize_title(title, uuid):
    additional_info = " (UUID = %s)" % uuid if uuid else ""
    return "-- %s%s --" % (title, additional_info)

def _visualize_sub_title(subtitle):
    return "-- %s --" % subtitle

def _visualize_item(item):
    return "  - %s" % item

def _visualize_sub_item(subitem):
    return "    - %s" % subitem

def _visualize_sub_sub_item(subsubitem):
    return "      - %s" % subsubitem

