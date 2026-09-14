:- set_prolog_flag(encoding, utf8).
:- multifile clausula_riesgosa/3.

clausula_riesgosa(Id, penalidad, critico) :-
    clausula(Id, penalidad, Texto),
    sub_atom(Texto, _, _, _, 'interes compuesto').

clausula_riesgosa(Id, rescision, alto) :-
    clausula(Id, rescision, Texto),
    \+ sub_atom(Texto, _, _, _, plazo),
    \+ sub_atom(Texto, _, _, _, notificacion).

clausula_riesgosa(Id, obligacion, critico) :-
    clausula(Id, obligacion, Texto),
    (   sub_atom(Texto, _, _, _, 'herencia futura')
    ;   sub_atom(Texto, _, _, _, 'prestacion imposible')
    ;   sub_atom(Texto, _, _, _, 'objeto ilicito')
    ).

clausula_riesgosa(Id, obligacion, critico) :-
    clausula(Id, obligacion, Texto),
    (   sub_atom(Texto, _, _, _, 'todos sus bienes')
    ;   sub_atom(Texto, _, _, _, 'renuncia a todos sus derechos')
    ).

clausula_riesgosa(Id, plazo, medio) :-
    clausula(Id, plazo, Texto),
    (   sub_atom(Texto, _, _, _, 'tiempo indefinido')
    ;   sub_atom(Texto, _, _, _, 'plazo abierto')
    ;   sub_atom(Texto, _, _, _, 'hasta nuevo aviso')
    ).

clausula_riesgosa(Id, confidencialidad, alto) :-
    clausula(Id, confidencialidad, Texto),
    \+ sub_atom(Texto, _, _, _, 'plazo de vigencia'),
    \+ sub_atom(Texto, _, _, _, 'vigencia de'),
    \+ sub_atom(Texto, _, _, _, anios),
    \+ sub_atom(Texto, _, _, _, meses),
    \+ sub_atom(Texto, _, _, _, termino).

clausula_valida_civil(Id) :-
    clausula(Id, Tipo, _),
    tipo_clausula(Tipo),
    \+ clausula_riesgosa(Id, _, _).
