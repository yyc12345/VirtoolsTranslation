import NlpUtils
import jsondiff
import sys

json1 = NlpUtils.LoadJsonFromFile(sys.argv[1])
json2 = NlpUtils.LoadJsonFromFile(sys.argv[2])

(_, value1, ) = NlpUtils.NlpJson2PlainJsonWrapper(json1)
(_, value2, ) = NlpUtils.NlpJson2PlainJsonWrapper(json2)

diff = jsondiff.diff(value1, value2)
print(diff)
