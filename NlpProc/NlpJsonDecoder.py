import NlpUtils
import jsondiff
import sys, collections

CmdArgvPair = collections.namedtuple('CmdArgvPair', ('nlpJson', 'trTemplate', 'trDiff', 'trIndex'))
def CmdArgvAnalyzer() -> tuple[CmdArgvPair]:
    ls: list[CmdArgvPair] = []

    argc = len(sys.argv) - 1
    if argc % 4 != 0:
        print("invalid parameter.")
        sys.exit(1)

    count = argc // 4
    return tuple(CmdArgvPair._make(sys.argv[1 + i * 4:5 + i * 4]) for i in range(count))

# script will order 1 file as reference
# 0. the nlp json file
# script will output 3 files for each version translation.
# 0. translation template json
# 0. the diff result comparing with the previous version
# 0. a list including the key of each value in template json
# so for a single version virtools, we need input 4 arguments
if __name__ == "__main__":
    resolvedArgv = CmdArgvAnalyzer()

    prevJson = None
    for vtVer in resolvedArgv:
        # read nlp json and convert it into plain json
        nlpJson = NlpUtils.LoadJson(vtVer.nlpJson)
        (plainKeys, plainValues, ) = NlpUtils.NlpJson2PlainJsonWrapper(nlpJson)

        # write index file
        NlpUtils.DumpTrIndex(vtVer.trIndex, plainKeys)

        # compare with previous one
        if prevJson is None:
            # this is first json. omit diff
            # write blank diff and write whole translation values
            NlpUtils.DumpTrDiff(vtVer.trDiff, [], [])
            NlpUtils.DumpTrTemplate(vtVer.trTemplate, dict(zip(plainKeys, plainValues)))
        else:
            # compare with prev json
            cmpResult = jsondiff.diff(prevJson, plainValues)
            # seperate diff result
            (insertedKey, deletedKey, insertedVal) = NlpUtils.SeperatePlainJsonDiff(cmpResult)

            # write diff
            NlpUtils.DumpTrDiff(vtVer.trDiff, insertedKey, deletedKey)
            # write template with special treat
            NlpUtils.DumpTrTemplate(vtVer.trTemplate, dict((i, j) for i, j in enumerate(insertedVal)))

        # assign prev json
        prevJson = plainValues

