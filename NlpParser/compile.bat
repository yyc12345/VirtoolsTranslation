antlr4 Nlp.g4
javac Nlp*.java
;grun Nlp document -tree < testbench.txt
java NlpRunner < ../NlpSrc/VT50.txt > result.json