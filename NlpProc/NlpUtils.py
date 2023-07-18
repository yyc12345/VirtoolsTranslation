import jsondiff
import collections
import io
import json
import re

g_EnableDebugging = False

g_VirtoolsVersion: tuple[str] = (
    '25', '30', '35', '40', '50',
)

if g_EnableDebugging:
    g_SupportedLangs: tuple[str] = (
        'template', 
    )
else:
    g_SupportedLangs: tuple[str] = (
        'zh-cn', 
    )

# ========== Basic File RW Functions ==========

def DumpJson(filepath: str, jsonData: dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(jsonData, f, 
            indent=2, 
            sort_keys=False,
            ensure_ascii=False
        )

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

def DumpTrDiff(filepath: str, insertedKey: list[int], deletedKey: list[int]):
    with open(filepath, 'w', encoding='utf-8') as f:
        for entryIdx in insertedKey:
            f.write(f'i/{entryIdx}\n')

        for entryIdx in deletedKey:
            f.write(f'd/{entryIdx}\n')

# return a tuple. (insertedKey, deletedKey)
def LoadTrDiff(filepath: str) -> tuple:
    insertedKey: list[int] = []
    deletedKey: list[int] = []
    with open(filepath, 'r', encoding='utf-8') as f:
        while True:
            ln = f.readline()
            if ln == '': break

            sp = ln.strip('\n').split('/')
            if sp[0] == 'i':
                insertedKey.append(int(sp[1]))
            else:
                deletedKey.append(int(sp[1]))

    return (insertedKey, deletedKey)

# return a tuple. (insertedKey, deletedKey, insertedVal)
def SeperatePlainJsonDiff(diffData: dict) -> tuple:
    insertedKey: list[int] = []
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

def CombinePlainJsonDiff(insertedKey: list[int], deletedKey: list[int], insertedVal: list[str]) -> dict:
    assert len(insertedKey) == len(insertedVal)

    result: dict = {}
    if len(insertedKey) != 0:
        result[jsondiff.insert] = []
    for k, v in zip(insertedKey, insertedVal):
        result[jsondiff.insert].append((k, v))
    
    if len(deletedKey) != 0:
        result[jsondiff.delete] = deletedKey[:]

    return result

# return a tuple. (keyList, valueList)
def NlpJson2PlainJson(nlpJson: dict) -> tuple:
    keyList: list[str] = []
    valueList: list[str] = []
    stack: collections.deque = collections.deque()
    InternalNlpJson2PlainJson(nlpJson, stack, keyList, valueList)
    return (keyList, valueList, )
def InternalNlpJson2PlainJson(nlpJson: dict, stack: collections.deque, keyList: list[str], valueList: list[str]):
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
            InternalNlpJson2PlainJson(entry, stack, keyList, valueList)
            stack.pop()

# ========== Json Converter ==========

def PlainJson2NlpJson(keyList: list[str], valueList: list[str]) -> dict:
    # create the base section
    # each section will have 3 k-v pair. language/section and entries are existed in original nlp json
    # and key_map is served for path finding and convenient for looking for sub section.
    result: dict = {
        "language": "English",
        "entries": [],
        "key_map": {}
    }
    # inerate list and construct dict
    for k, v in zip(keyList, valueList):
        InternalPlainJson2NlpJson(result, k, v)
    return result
def RemoveKeyMapInGeneratedNlpJson(nlpJson: dict) -> dict:
    # remove useless key map
    InternalDelNlpJsonKeyMap(nlpJson)
    return nlpJson
def InternalDelNlpJsonKeyMap(nlpJson: dict):
    # recursively calling self
    for v in nlpJson['key_map'].values():
        InternalDelNlpJsonKeyMap(v)
    # then delete self
    del nlpJson['key_map']
def InternalPlainJson2NlpJson(nlpJson: dict, pairKey: str, pairVal: str):
    keypath = pairKey.split('/')
    # confirm last node is number and remove it
    assert keypath[-1].isdecimal()
    keypath = keypath[:-1]

    # move to correct sub section
    for pathpart in keypath:
        if pathpart in nlpJson['key_map']:
            # existed sub section. directly entering
            nlpJson = nlpJson['key_map'][pathpart]
        else:
            # create a new one
            sub_section = {
                'section': pathpart,
                'entries': [],
                'key_map': {}
            }

            # add into current section
            nlpJson['entries'].append(sub_section)
            nlpJson['key_map'][pathpart] = sub_section

            # move to the new created sub section
            nlpJson = sub_section

    # insert data
    nlpJson['entries'].append(pairVal)

# ========== Raw Nlp Text Writer ==========

def DumpNlpJson(filepath: str, encoding: str, lang_macro: str, nlpJson: dict):
    # write in wb mode because we need explicitly write \r\n, not \n
    with open(filepath, 'wb') as f:
        f.write(f'Language:{lang_macro}\r\n'.encode(encoding, errors='ignore'))
        InternalDumpNlpJson(f, encoding, 0, nlpJson)

# g_NlpJsonStrRepl1 = re.compile('\\\\')
g_NlpJsonStrRepl2 = re.compile('\"')
def NlpJsonStringProcessor(strl: str) -> str:
    return g_NlpJsonStrRepl2.sub('\"\"', strl)

def InternalDumpNlpJson(f: io.BufferedWriter, encoding: str, depth: int, nlpJson: dict):
    assert 'entries' in nlpJson

    is_first: bool = True
    for entity in nlpJson['entries']:
        if isinstance(entity, str):
            # write comma if not the first element
            if not is_first: f.write(','.encode(encoding))
            else: is_first = False

            # write real data
            # replace all " to "" to escape
            f.write('"{0}"'.format(NlpJsonStringProcessor(entity)).encode(encoding, errors='ignore'))
        else:
            # sub section
            # write section header and call self.
            if depth == 0:
                f.write(f'\r\n[{entity["section"]}]\r\n'.encode(encoding, errors='ignore'))
            else:
                f.write(f'\r\n<{entity["section"]}>\r\n'.encode(encoding, errors='ignore'))

            InternalDumpNlpJson(f, encoding, depth + 1, entity)

