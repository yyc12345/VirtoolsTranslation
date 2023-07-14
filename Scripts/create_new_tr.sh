if [ $# -ne 1 ]
then
    echo "[ERR] invalid arguments"
    echo "Syntax"
    echo ""
    echo "./create_new_tr.sh <lang-symbol>"
    echo "<lang-symbol>: your preferred language symbol. such as en, de, zh-cn..."
    exit 1
fi

cd NlpTr
cp VT25.template.json "VT25."$1".json"
cp VT35.template.json "VT35."$1".json"
cp VT40.template.json "VT40."$1".json"
cp VT50.template.json "VT50."$1".json"
cd ..
echo "DONE"
