./NlpEncoder/out/NlpEncoder uncompress NlpSrc/VT25.nlp NlpSrc/VT25.txt
./NlpEncoder/out/NlpEncoder uncompress NlpSrc/VT35.nlp NlpSrc/VT35.txt
./NlpEncoder/out/NlpEncoder uncompress NlpSrc/VT40.nlp NlpSrc/VT40.txt
./NlpEncoder/out/NlpEncoder uncompress NlpSrc/VT50.nlp NlpSrc/VT50.txt

cd NlpParser
java NlpRunner ../NlpSrc/VT25.txt ../NlpSrc/VT25.json
java NlpRunner ../NlpSrc/VT35.txt ../NlpSrc/VT35.json
java NlpRunner ../NlpSrc/VT40.txt ../NlpSrc/VT40.json
java NlpRunner ../NlpSrc/VT50.txt ../NlpSrc/VT50.json
cd ..