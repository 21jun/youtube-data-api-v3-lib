from util.load import load_keys

DEVELOPER_AUTH_LIST = []
DEVELOPER_KEY_LIST = []
for developer in load_keys():
    DEVELOPER_KEY_LIST.append(developer['apikey'])
    DEVELOPER_AUTH_LIST.append(developer['id/pw'])
