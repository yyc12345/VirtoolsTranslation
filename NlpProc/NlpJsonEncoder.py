import NlpUtils
import jsondiff
import collections

g_SupportedEncoding = {
    'zh-cn': ('utf-8', 'gb2312', )
}

VtTrDataTuple = collections.namedtuple('VtTrDataTuple', ('rawNlp', 'trTemplate', 'trDiff', 'trIndex'))
def GetRawNlpPath(ver: str, lang: str) -> str:
    return f'../NlpTr/out/VT{ver}.{lang}.txt'
def GetTrPath(ver: str, lang: str) -> str:
    return f'../NlpTr/VT{ver}.{lang}.json'
def GetTrDiffPath(ver: str) -> str:
    return f'../NlpTr/VT{ver}.diff'
def GetTrIndexPath(ver: str) -> str:
    return f'../NlpTr/VT{ver}.index'

if __name__ == "__main__":

    for ver in NlpUtils.g_VirtoolsVersion:
        # load diff and index data

        for lang in NlpUtils.g_SupportedLangs:
            # load lang file

            # patch it

            # convert plain json to nested json

            # write into file with different encoding
            for enc in g_SupportedEncoding[lang]:
                print(f'Process {ver}.{lang}.{enc}...')
