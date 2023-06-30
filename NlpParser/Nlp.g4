grammar Nlp;

// ===== Parser =====

document: LANG_HEADER (section)* ;

section: SECTION_HEAD (subSection | entry)* ;

subSection: SUB_SECTION_HEAD (entry)* ;

entry: ENTRY_STRING                             # entryString
| ENTRY_STRING (LINE_CONCATOR ENTRY_STRING)+    # entryConcatedString
| ENTRY_INTEGER                                 # entryInteger
;

// ===== Lexer =====

LANG_HEADER: 'Language:' [a-zA-Z]+ ;

SECTION_HEAD: '[' NAME_SECTION ']' ;
SUB_SECTION_HEAD: '<' NAME_SECTION '>' ;
fragment NAME_SECTION: [ a-zA-Z0-9]+ ;   // section name are consisted of space, char and number

ENTRY_STRING: '"' (ENTRY_STRING_ESC| ~'"' )* '"' ;
fragment ENTRY_STRING_ESC: '""' | '\\\\' | '\\t' | '\\n' ; 

ENTRY_INTEGER: [1-9][0-9]+ ;

LINE_CONCATOR: '\\';
SPLITTOR: [ ,;\r\n]+ -> skip;               // ignore all splittor and space
LINE_COMMENT: '//' ~[\r\n]* -> skip ;       // consume all non-line-breaker. because we need line breaker.
BLOCK_COMMENT: '/*' .*? '*/' -> skip ;
