from typing import List


def load_keys(path='APIKEYLIST.txt'):
    with open(path) as f:
        keys = f.readlines()
    key_list: List[str] = [{'apikey': key.split()[0], 'id/pw': ' '.join(key.split()[1:])} for key in keys]
    return key_list


def load_search_list(path='SEARCHLIST.txt'):
    with open(path, 'rt', encoding='UTF8') as f:
        games = f.readlines()
    game_list: List[str] = [{'appid': game.split()[0], 'name': ' '.join(game.split()[1:])} for game in games]
    return game_list


if __name__ == '__main__':
    print(load_search_list())
