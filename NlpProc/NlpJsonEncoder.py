import NlpUtils
import jsondiff
import collections

if NlpUtils.g_EnableDebugging:
    g_SupportedEncoding = {
        'template': ('English', ('windows-1252', ), )
    }
else:
    g_SupportedEncoding = {
        'zh-cn': ('Chinese', ('utf-8', 'gb2312', ), )
    }

VtTrDataTuple = collections.namedtuple('VtTrDataTuple', ('rawNlp', 'trTemplate', 'trDiff', 'trIndex'))
def GetNlpJsonPath(ver: str, lang: str) -> str:
    return f'../NlpTr/out/VT{ver}.{lang}.json'
def GetRawNlpPath(ver: str, lang: str, enc: str) -> str:
    return f'../NlpTr/out/VT{ver}.{lang}.{enc}.txt'
def GetTrPath(ver: str, lang: str) -> str:
    return f'../NlpTr/VT{ver}.{lang}.json'
def GetTrDiffPath(ver: str) -> str:
    return f'../NlpTr/VT{ver}.diff'
def GetTrIndexPath(ver: str) -> str:
    return f'../NlpTr/VT{ver}.index'

g_CriticalFields: dict[str, str] = {
    'Common/Registry/0': 'Software\\\\Virtools\\\\Global',
    'Common/Registry/1': 'Usage Count',
    'Common/Timebomb/0': 'Key1',
    'Common/Timebomb/1': 'Key2',
    'Common/Timebomb/2': 'Key3',
    'Common/Timebomb/3': 'SYSINFO.SysInfo32\\\\CLSID',
    'Common/Timebomb/4': '\\\\csrsrv32.dll',
    '3D Layout/Registry/0': 'Software\\\\NeMo\\\\3D Layout',
}
def CriticalFieldChecker(nlpJson: dict):
    corrected: bool = False
    for k, v in g_CriticalFields.items():
        # analyze path and find the node
        path = k.split('/')
        assert path[-1].isdecimal()
        path_terminal = int(path[-1])
        path = path[:-1]

        node = nlpJson
        for pathpart in path:
            node = node['key_map'][pathpart]

        # check it
        if node['entries'][path_terminal] != v:
            # if not matched. correct it
            node['entries'][path_terminal] = v
            # and notify it
            corrected = True

    if corrected:
        print('Some critical filed was changed in tr by accident. We have corrected them, but please check tr carefully')

if __name__ == "__main__":

    # load each version's diff data and patch data for conventient using
    PreLoadedDiffIdxTuple = collections.namedtuple('PreLoadedDiffIndexTuple', ('insertedKey', 'deletedKey', 'plainKeys'))
    preLoadedData: dict[str, PreLoadedDiffIdxTuple] = {}
    for ver in NlpUtils.g_VirtoolsVersion:
        # load diff and index data
        insertedKey, deletedKey = NlpUtils.LoadTrDiff(GetTrDiffPath(ver))
        plainKeys = NlpUtils.LoadTrIndex(GetTrIndexPath(ver))
        # insert to dict
        preLoadedData[ver] = PreLoadedDiffIdxTuple._make((insertedKey, deletedKey, plainKeys))

    # iterate lang first
    # because we use progressive patch. we need iterate vt ver in order for each single languages
    for lang in NlpUtils.g_SupportedLangs:
        
        prevPlainValues: list[str] = None
        for ver in NlpUtils.g_VirtoolsVersion:
            print(f'Loading {ver}.{lang}...')

            # pick data from pre-loaded dict
            diffIdxData = preLoadedData[ver]
            plainKeys = diffIdxData.plainKeys

            # load lang file
            # and only keeps its value.
            trFull = NlpUtils.LoadTrTemplate(GetTrPath(ver, lang))
            _, plainValues = zip(*trFull.items())

            # patch it if needed
            if prevPlainValues is not None:
                # patch needed load
                # load patch part first
                trPart = NlpUtils.LoadTrTemplate(GetTrPath(ver, lang))

                # re-construct the diff structure understood by jsondiff
                cmpResult = NlpUtils.CombinePlainJsonDiff(diffIdxData.insertedKey, diffIdxData.deletedKey, plainValues)

                # patch data
                plainValues = jsondiff.patch(prevPlainValues, cmpResult)

            # convert plain json to nlp json
            nlpJson = NlpUtils.PlainJson2NlpJson(plainKeys, plainValues)
            # check some critical fields
            CriticalFieldChecker(nlpJson)

            if NlpUtils.g_EnableDebugging:
                NlpUtils.RemoveKeyMapInGeneratedNlpJson(nlpJson)
                NlpUtils.DumpJson(GetNlpJsonPath(ver, lang), nlpJson)

            # write into file with different encoding
            lang_macro, encs = g_SupportedEncoding[lang]
            for enc in encs:
                print(f'Processing {ver}.{lang}.{enc}...')
                NlpUtils.DumpNlpJson(GetRawNlpPath(ver, lang, enc), enc, lang_macro, nlpJson)

            # assign prev json
            prevPlainValues = plainValues