:- set_prolog_flag(encoding, utf8).
:- multifile clausula_riesgosa/3.

clausula_riesgosa(Id, confidencialidad, alto) :-
    clausula(Id, confidencialidad, Texto),
    \+ sub_atom(Texto, _, _, _, 'plazo de vigencia'),
    \+ sub_atom(Texto, _, _, _, 'vigente por'),
    \+ sub_atom(Texto, _, _, _, anios),
    \+ sub_atom(Texto, _, _, _, meses).

clausula_riesgosa(Id, penalidad, medio) :-
    clausula(Id, penalidad, Texto),
    sub_atom(Texto, _, _, _, 'exclusividad absoluta').

clausula_riesgosa(Id, general, alto) :-
    clausula(Id, general, Texto),
    (   sub_atom(Texto, _, _, _, 'arbitraje en')
    ;   sub_atom(Texto, _, _, _, 'jurisdiccion extranjera')
    ),
    \+ sub_atom(Texto, _, _, _, 'Peru').

clausula_riesgosa(Id, penalidad, alto) :-
    clausula(Id, penalidad, Texto),
    (   sub_atom(Texto, _, _, _, 'sin limite')
    ;   sub_atom(Texto, _, _, _, 'sin tope')
    ;   sub_atom(Texto, _, _, _, ilimitada)
    ).

clausula_riesgosa(Id, confidencialidad, critico) :-
    clausula(Id, confidencialidad, Texto),
    (   sub_atom(Texto, _, _, _, 'ceder la informacion a terceros')
    ;   sub_atom(Texto, _, _, _, 'transferir datos a terceros')
    ;   sub_atom(Texto, _, _, _, 'venta de datos')
    ).

clausula_riesgosa(Id, obligacion, critico) :-
    clausula(Id, obligacion, Texto),
    (   sub_atom(Texto, _, _, _, 'modificar el precio unilateralmente')
    ;   sub_atom(Texto, _, _, _, 'cambiar las condiciones sin aviso')
    ).

clausula_valida_comercial(Id) :-
    clausula(Id, Tipo, _),
    tipo_clausula(Tipo),
    \+ clausula_riesgosa(Id, _, _).
