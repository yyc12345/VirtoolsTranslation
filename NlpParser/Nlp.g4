grammar Nlp;

nlp_document: LANG_HEADER (section)* ;

section: SECTION_HEAD (sub_section | entry)* ;

sub_section: SUB_SECTION_HEAD (entry)* ;

entry: ENTRY_STRING                             # entry_string_t
| ENTRY_STRING (LINE_CONCAT ENTRY_STRING)+      # entry_concated_string_t
| ENTRY_INTEGER                                 # entry_integer_t
;

LANG_HEADER: 'Language:' [a-zA-Z]+ ;

SECTION_HEAD: '[' NAME_SECTION ']' ;
SUB_SECTION_HEAD: '<' NAME_SECTION '>' ;
fragment NAME_SECTION: [ a-zA-Z0-9]+ ;   // section name are consisted of space, char and number

ENTRY_STRING: '"' (STRING_ESC|.)*? '"' ;
fragment STRING_ESC: '\\"' | '\\\\' ; 

ENTRY_INTEGER: [1-9][0-9]+ ;

SPLITTOR: [ ,;\r\n]+ -> skip;               // ignore all splittor and space
LINE_CONCAT: '\\' ;
LINE_COMMENT: '//' ~[\r\n]* -> skip ;       // consume all non-line-breaker. because we need line breaker.
BLOCK_COMMENT: '/*' .*? '*/' -> skip ;