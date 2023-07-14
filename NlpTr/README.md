# Nlp Translation

## Create New Language Translation

These parts almost are done by repository maintainer. This is just a manual when maintainer goes.

0. First, decide your preferred language macro. I take "zh-cn" in there for example.
0. Executing `./Scripts/create_new_tr.sh "zh-cn"` in **ROOT** folder.
0. You will get a bunch of language json file named like "VT25.zh-cn.json" and listed in NlpTr folder.
0. Then navigate to NlpProc folder and register your language macro.
    - `NlpUtils.py`: Add your language macro as a entry in the second declaration of `g_SupportedLangs`.
    - `NlpJsonEncoder.py`: Navigate to the second declaration of `g_SupportedEncoding` In Add your macro, specify the language name shown in Virtools and, a tuple of common encoding of your language. Please note that UTF8 encoding is necessary for each language.

## How to Edit Translation

Choose your preferred translator, and fill the json correctly. I use Poedit anyway.

## How to Compile Translation

0. Executing `./Scripts/compile_tr.sh` in **ROOT** folder.
0. Then all nlp files should be generated in NlpTr/out
