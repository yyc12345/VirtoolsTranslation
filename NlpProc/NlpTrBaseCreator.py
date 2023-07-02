import NlpUtils
import sys, collections

def CreateBaseJsonWrapper(baseJson: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    stack: collections.deque = collections.deque()
    CreateBaseJson(baseJson, stack, result)
    return result
def CreateBaseJson(baseJson: dict, stack: collections.deque, result: dict[str, str]):
    assert isinstance(baseJson, dict)
    assert 'entries' in baseJson

    counter = 0
    for entry in baseJson['entries']:
        if isinstance(entry, str):
            result['.'.join(tuple(stack) + (str(counter), ))] = entry
            counter += 1
        else:
            stack.append(entry['section'])
            CreateBaseJson(entry, stack, result)
            stack.pop()

if __name__ == "__main__":
    baseJson = NlpUtils.LoadJsonFromFile(sys.argv[1])
    trJson = CreateBaseJsonWrapper(baseJson)
    NlpUtils.WriteJsonToFile(sys.argv[2], trJson)
