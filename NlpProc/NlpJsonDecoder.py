import NlpUtils
import jsondiff
import collections

VtTrDataTuple = collections.namedtuple('VtTrDataTuple', ('nlpJson', 'trTemplate', 'trDiff', 'trIndex'))
def ConstructVtTrDataTuple() -> tuple[VtTrDataTuple]:
    return tuple(VtTrDataTuple._make((
        f'../NlpSrc/VT{i}.json',
        f'../NlpTr/VT{i}.template.json',
        f'../NlpTr/VT{i}.diff',
        f'../NlpTr/VT{i}.index',
    ))for i in NlpUtils.g_VirtoolsVersion)

if __name__ == "__main__":

    prevPlainValues = None
    for vtVer in ConstructVtTrDataTuple():
        print(f'Processing {vtVer.nlpJson}...')

        # read nlp json and convert it into plain json
        nlpJson = NlpUtils.LoadJson(vtVer.nlpJson)
        (plainKeys, plainValues, ) = NlpUtils.NlpJson2PlainJson(nlpJson)

        # write index file
        NlpUtils.DumpTrIndex(vtVer.trIndex, plainKeys)

        # compare with previous one
        if prevPlainValues is None:
            # this is first json. omit diff
            # write blank diff and write whole translation values
            NlpUtils.DumpTrDiff(vtVer.trDiff, [], [])
            NlpUtils.DumpTrTemplate(vtVer.trTemplate, dict(zip(plainKeys, plainValues)))
        else:
            # compare with prev json
            cmpResult = jsondiff.diff(prevPlainValues, plainValues)
            # seperate diff result
            (insertedKey, deletedKey, insertedVal) = NlpUtils.SeperatePlainJsonDiff(cmpResult)

            # write diff
            NlpUtils.DumpTrDiff(vtVer.trDiff, insertedKey, deletedKey)
            # write template with special treat
            NlpUtils.DumpTrTemplate(vtVer.trTemplate, dict((plainKeys[insertedKey[i]], insertedVal[i]) for i in range(len(insertedKey))))

        # assign prev json
        prevPlainValues = plainValues

