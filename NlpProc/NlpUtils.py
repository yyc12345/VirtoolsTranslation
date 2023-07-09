import jsondiff
import collections
import io
import json

def DumpJson(filepath: str, jsonData: dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(jsonData, f, indent=4, sort_keys=False)

def LoadJson(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def DumpTrIndex(filepath: str, indexData: list[str]):
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in indexData:
            f.write(item)
            f.write('\n')

def LoadTrIndex(filepath: str) -> list[str]:
    data: list[str] = []
    with open(filepath, 'r', encoding='utf-8') as f:
        while True:
            ln = f.readline()
            if ln == '': break
            data.append(ln.strip('\n'))

    return data

def DumpTrTemplate(filepath: str, templateData: dict[str, str]):
    DumpJson(filepath, templateData)

def LoadTrTemplate(filepath: str) ->  dict[str, str]:
    return LoadJson(filepath)

def DumpTrDiff(filepath: str, insertedKey: list[str], deletedKey: list[str]):
    with open(filepath, 'w', encoding='utf-8') as f:
        for entryIdx in insertedKey:
            f.write(f'i/{entryIdx}\n')

        for entryIdx in deletedKey:
            f.write(f'd/{entryIdx}\n')

# return a tuple. (insertedKey, deletedKey)
def LoadTrDiff(filepath: str) -> dict:
    insertedKey: list[str] = []
    deletedKey: list[str] = []
    with open(filepath, 'r', encoding='utf-8') as f:
        while True:
            ln = f.readline()
            if ln == '': break

            sp = ln.strip('\n').split('/')
            if sp[0] == 'i':
                insertedKey.append(sp[1])
            else:
                deletedKey.append(sp[1])

    return (insertedKey, deletedKey)

# return a tuple. (insertedKey, deletedKey, insertedVal)
def SeperatePlainJsonDiff(diffData: dict) -> tuple:
    insertedKey: list[str] = []
    insertedVal: list[str] = []

    if jsondiff.insert in diffData:
        for (entryIdx, entryVal, ) in diffData[jsondiff.insert]:
            insertedKey.append(entryIdx)
            insertedVal.append(entryVal)

    if jsondiff.delete in diffData:
        deletedKey = diffData[jsondiff.delete][:]
    else:
        deletedKey = []

    return (insertedKey, deletedKey, insertedVal)

# return a tuple. (keyList, valueList)
def NlpJson2PlainJsonWrapper(nlpJson: dict) -> tuple:
    keyList: list[str] = []
    valueList: list[str] = []
    stack: collections.deque = collections.deque()
    NlpJson2PlainJson(nlpJson, stack, keyList, valueList)
    return (keyList, valueList, )
def NlpJson2PlainJson(nlpJson: dict, stack: collections.deque, keyList: list[str], valueList: list[str]):
    assert isinstance(nlpJson, dict)
    assert 'entries' in nlpJson

    counter = 0
    for entry in nlpJson['entries']:
        if isinstance(entry, str):
            # is data node. add into result
            keyList.append('/'.join(tuple(stack) + (str(counter), )))
            valueList.append(entry)
            counter += 1
        else:
            # is a sub section
            # push section name and recursive calling this function
            stack.append(entry['section'])
            NlpJson2PlainJson(entry, stack, keyList, valueList)
            stack.pop()

