import NlpUtils
import jsondiff
import collections

if NlpUtils.g_EnableDebugging:
    g_SupportedEncoding = {
        'template': ('English', ('ascii', ), )
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
    # because we use progressive patch. we need iterate vt ver in order
    for lang in NlpUtils.g_SupportedLangs:
        
        prevPlainValues: list[str] = None
        for ver in NlpUtils.g_VirtoolsVersion:
            print(f'Processing {ver}.{lang}...')

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

            if NlpUtils.g_EnableDebugging:
                NlpUtils.DumpJson(GetNlpJsonPath(ver, lang), nlpJson)

            # write into file with different encoding
            lang_macro, encs = g_SupportedEncoding[lang]
            for enc in encs:
                print(f'Processing {ver}.{lang}.{enc}...')
                NlpUtils.DumpNlpJson(GetRawNlpPath(ver, lang, enc), enc, lang_macro, nlpJson)

            # assign prev json
            prevPlainValues = plainValues