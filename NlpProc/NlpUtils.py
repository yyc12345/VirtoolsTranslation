import jsondiff
import collections
import io
import json

def WriteJsonToFile(filepath: str, jsonData: dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(jsonData, f, indent=4, sort_keys=False)

def LoadJsonFromFile(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def SaveDiffToFileWrapper(jsonDiffData: dict, filepath: str) -> dict[str, str]:
    result: dict[tuple[int], str] = {}
    stack: collections.deque = collections.deque()
    with open(filepath, 'w', encoding='utf-8') as fdiff:
        SaveDiffToFile(jsonDiffData, fdiff, stack, result)
    return result

def SaveDiffToFile(jsonDiffData: dict, fs: io.TextIOWrapper, stack: collections.deque, result: dict[tuple[int], str]):
    assert isinstance(jsonDiffData, dict)
    assert len(jsonDiffData) == 1
    assert "entries" in jsonDiffData
    assert isinstance(jsonDiffData["entries"], dict)

    for key, item in jsonDiffData["entries"].items():
        if isinstance(key, int):
            stack.append(key)
            SaveDiffToFile(item, fs, stack, result)
            stack.pop()
        elif key == jsondiff.symbols.insert:
            for (modIdx, modEntry) in item:
                stridx = ".".join(tuple(stack) + (modIdx, ))
                result[stridx] = modEntry
                fs.write(f'i {stridx}\n')
        elif key == jsondiff.symbols.delete:
            for delIdx in item:
                stridx = ".".join(tuple(stack) + (delIdx, ))
                fs.write(f'd {stridx}\n')
        else:
            raise Exception("invalid key type")

def ReadDiffFromFile(translations: tuple[str], filepath: str, result: dict):
    pass

