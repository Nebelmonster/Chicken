import math


def get_level(user_id, data):
    xp = data["counters"][str(user_id)]["msgs"]["xp"]
    return int(math.sqrt(xp / 160) + 1)


def get_next_level_thresh(user_id,  data):
    next_level = get_level(user_id, data) + 1
    next_level_threshold = 160 * math.pow(next_level - 1, 2)
    return int(next_level_threshold)