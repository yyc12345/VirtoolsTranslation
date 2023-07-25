cd NlpTr
mkdir out
cd ../NlpProc
python3 NlpJsonEncoder.py
cd ..

cd NlpTr/out
for file in *.txt
do
	if test -f $file
	then
		txt_file=$file
		nlp_file=$(basename $file .txt)".nlp"
		../../NlpCodec/out/NlpCodec encode $txt_file $nlp_file
	fi
done
cd ../..
