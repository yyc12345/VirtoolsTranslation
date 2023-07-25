# Virtools Translation

Provide I18N for an abandoned ancient game-making software - Virtools.

This repository consist of these parts:

* NlpCodec: The codec about encoding and decoding NLP translation file used by Virtools.
* NlpParser: An ANTLR written parser which can recognised decoded NLP text file syntax and convert it to a neasted JSON format because JSON format is more common.
* NlpProc
  - Convert the JSON between the nested JSON output by NlpParser and un-nested JSON (flat JSON / plain JSON) to let it more acceptable for the most of common I18N software.
  - Output NLP text file when compiling translation.

## How to Translate

I take `zh-cn` (Chinese) as a example. Navigate to NlpTr folder first. and you will find following files.

* `VT25.zh-cn.json`
* `VT30.zh-cn.json`
* `VT35.zh-cn.json`
* `VT40.zh-cn.json`
* `VT50.zh-cn.json`

The only things you need to do is translate these JSON files.

## How to Add Language

Contact the owner of repository, or follow the manual `NlpTr/README.md` when owner went off.

## How the Files Generated in NlpTr

This section is not suit for beginner.

0. Run `./Scripts/compile_codec.sh` to compile NlpCodec
0. Run `./Scripts/compile_parser.sh` to compile NlpParser
0. Run `./Scripts/generate_source.sh` to generate the files located in NlpTr.

## How We Generate NLP Files when Publishing

This section is not suit for beginner.

0. Run `./Scripts/compile_codec.sh` to compile NlpCodec. Skip if you have compiled.
0. Run `./Scripts/compile_tr.sh`

## Can I Use This on Windows

Use MSYS2.
