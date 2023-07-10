import NlpUtils
import jsondiff
import sys

json1 = NlpUtils.LoadJson(sys.argv[1])
json2 = NlpUtils.LoadJson(sys.argv[2])

(_, value1, ) = NlpUtils.NlpJson2PlainJson(json1)
(_, value2, ) = NlpUtils.NlpJson2PlainJson(json2)

diff = jsondiff.diff(value1, value2)
print(diff)
