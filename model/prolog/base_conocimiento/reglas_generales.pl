:- set_prolog_flag(encoding, utf8).
:- multifile clausula_riesgosa/3.

clausula_riesgosa(Id, penalidad, alto) :-
    clausula(Id, penalidad, Texto),
    (   sub_atom(Texto, _, _, _, 'penalidad')
    ;   sub_atom(Texto, _, _, _, 'multa')
    ),
    (   sub_atom(Texto, _, _, _, 'sin tope')
    ;   sub_atom(Texto, _, _, _, 'sin limite')
    ;   sub_atom(Texto, _, _, _, '40%')
    ).

clausula_riesgosa(Id, penalidad, critico) :-
    clausula(Id, penalidad, Texto),
    (   sub_atom(Texto, _, _, _, 'interes compuesto')
    ;   sub_atom(Texto, _, _, _, 'interes acumulado')
    ).

clausula_riesgosa(Id, penalidad, critico) :-
    clausula(Id, penalidad, Texto),
    (   sub_atom(Texto, _, _, _, '50%')
    ;   sub_atom(Texto, _, _, _, '60%')
    ;   sub_atom(Texto, _, _, _, '70%')
    ;   sub_atom(Texto, _, _, _, '80%')
    ;   sub_atom(Texto, _, _, _, '90%')
    ;   sub_atom(Texto, _, _, _, '100%')
    ).


clausula_riesgosa(Id, plazo, medio) :-
    clausula(Id, plazo, Texto),
    \+ sub_atom(Texto, _, _, _, dias),
    \+ sub_atom(Texto, _, _, _, meses),
    \+ sub_atom(Texto, _, _, _, semanas),
    \+ sub_atom(Texto, _, _, _, anios),
    \+ sub_atom(Texto, _, _, _, 'años').

clausula_riesgosa(Id, rescision, alto) :-
    clausula(Id, rescision, Texto),
    \+ sub_atom(Texto, _, _, _, preaviso),
    \+ sub_atom(Texto, _, _, _, notificacion),
    \+ sub_atom(Texto, _, _, _, 'aviso previo').

clausula_riesgosa(Id, general, critico) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'no sera responsable')
    ;   sub_atom(Texto, _, _, _, 'exime de responsabilidad')
    ;   sub_atom(Texto, _, _, _, 'exonera de responsabilidad')
    ;   sub_atom(Texto, _, _, _, 'sin responsabilidad alguna')
    ;   sub_atom(Texto, _, _, _, 'renuncia a reclamar')
    ).

clausula_riesgosa(Id, general, alto) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'a sola decision')
    ;   sub_atom(Texto, _, _, _, 'a su sola discrecion')
    ;   sub_atom(Texto, _, _, _, 'sin necesidad de causa')
    ).

clausula_incompleta(Id) :-
    clausula(Id, _, Texto),
    atom_length(Texto, Len),
    Len < 15.

contrato_valido :-
    \+ clausula_riesgosa(_, _, critico).

clausula_riesgosa(Id, no_competencia, alto) :-
    clausula(Id, no_competencia, Texto),
    (   sub_atom(Texto, _, _, _, 'cinco anos')
    ;   sub_atom(Texto, _, _, _, 'seis meses')
    ;   sub_atom(Texto, _, _, _, 'un ano')
    ).

clausula_riesgosa(Id, no_competencia, critico) :-
    clausula(Id, no_competencia, Texto),
    (   sub_atom(Texto, _, _, _, 'sin compensacion')
    ;   sub_atom(Texto, _, _, _, 'todo el pais')
    ;   sub_atom(Texto, _, _, _, 'diez anos')
    ;   sub_atom(Texto, _, _, _, 'exclusividad absoluta')
    ).

clausula_riesgosa(Id, no_competencia, alto) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'exclusividad absoluta')
    ;   sub_atom(Texto, _, _, _, 'queda prohibido prestar servicios')
    ;   sub_atom(Texto, _, _, _, 'a terceras personas')
    ),
    \+ sub_atom(Texto, _, _, _, compensacion).

clausula_riesgosa(Id, propiedad_intelectual, alto) :-
    clausula(Id, propiedad_intelectual, Texto),
    (   sub_atom(Texto, _, _, _, 'pasara automaticamente')
    ;   sub_atom(Texto, _, _, _, 'sin pago adicional')
    ;   sub_atom(Texto, _, _, _, 'todo derecho')
    ).

clausula_riesgosa(Id, propiedad_intelectual, critico) :-
    clausula(Id, propiedad_intelectual, Texto),
    (   sub_atom(Texto, _, _, _, 'codigo fuente')
    ;   sub_atom(Texto, _, _, _, 'derechos perpetuos')
    ;   sub_atom(Texto, _, _, _, 'irrevocable y exclusiva')
    ;   sub_atom(Texto, _, _, _, 'irrevocable')
    ;   sub_atom(Texto, _, _, _, 'perpetua')
    ;   sub_atom(Texto, _, _, _, 'mundial')
    ).

clausula_riesgosa(Id, propiedad_intelectual, alto) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'propiedad intelectual')
    ;   sub_atom(Texto, _, _, _, 'derechos de autor')
    ),
    (   sub_atom(Texto, _, _, _, 'sin regal')
    ;   sub_atom(Texto, _, _, _, 'sin pago adicional')
    ;   sub_atom(Texto, _, _, _, 'sin derecho a creditos')
    ;   sub_atom(Texto, _, _, _, 'mencion publica')
    ).

clausula_riesgosa(Id, datos_personales, alto) :-
    clausula(Id, datos_personales, Texto),
    (   sub_atom(Texto, _, _, _, 'terceros')
    ;   sub_atom(Texto, _, _, _, 'compartir datos')
    ;   sub_atom(Texto, _, _, _, 'publicar la deuda')
    ).

clausula_riesgosa(Id, datos_personales, critico) :-
    clausula(Id, datos_personales, Texto),
    (   sub_atom(Texto, _, _, _, 'datos biometricos')
    ;   sub_atom(Texto, _, _, _, 'sin consentimiento')
    ;   sub_atom(Texto, _, _, _, 'redes sociales')
    ).

clausula_riesgosa(Id, arbitraje, alto) :-
    clausula(Id, arbitraje, Texto),
    (   sub_atom(Texto, _, _, _, 'obligatorio')
    ;   sub_atom(Texto, _, _, _, 'exclusivamente')
    ;   sub_atom(Texto, _, _, _, 'ad hoc designado por el vendedor')
    ).

clausula_riesgosa(Id, arbitraje, critico) :-
    clausula(Id, arbitraje, Texto),
    (   sub_atom(Texto, _, _, _, 'renunciando a la via judicial')
    ;   sub_atom(Texto, _, _, _, 'solo por arbitraje privado')
    ;   sub_atom(Texto, _, _, _, 'renuncian de forma expresa a los fueros')
    ;   sub_atom(Texto, _, _, _, 'elegidas por el cliente')
    ).

clausula_riesgosa(Id, arbitraje, alto) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'cortes arbitrales')
    ;   sub_atom(Texto, _, _, _, 'instancias internacionales')
    ),
    (   sub_atom(Texto, _, _, _, 'costos legales')
    ;   sub_atom(Texto, _, _, _, 'honorarios profesionales')
    ;   sub_atom(Texto, _, _, _, 'sufragar la totalidad')
    ).

clausula_riesgosa(Id, modificacion_unilateral, alto) :-
    clausula(Id, modificacion_unilateral, Texto),
    (   sub_atom(Texto, _, _, _, 'modificar unilateralmente')
    ;   sub_atom(Texto, _, _, _, 'variar unilateralmente')
    ;   sub_atom(Texto, _, _, _, 'sin acuerdo')
    ).

clausula_riesgosa(Id, modificacion_unilateral, critico) :-
    clausula(Id, modificacion_unilateral, Texto),
    (   sub_atom(Texto, _, _, _, 'sin aviso previo')
    ;   sub_atom(Texto, _, _, _, 'a su sola discrecion')
    ;   sub_atom(Texto, _, _, _, 'sin acuerdo del proveedor')
    ).

clausula_riesgosa(Id, rescision, critico) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'sin necesidad de justificacion')
    ;   sub_atom(Texto, _, _, _, 'sin expresion de causa')
    ;   sub_atom(Texto, _, _, _, 'con efecto inmediato')
    ),
    (   sub_atom(Texto, _, _, _, 'no dara derecho a indemnizaciones')
    ;   sub_atom(Texto, _, _, _, 'ni reembolsos')
    ;   sub_atom(Texto, _, _, _, 'no aprobados expresamente')
    ).

clausula_riesgosa(Id, penalidad, alto) :-
    clausula(Id, _, Texto),
    (   sub_atom(Texto, _, _, _, 'mantendra indemne')
    ;   sub_atom(Texto, _, _, _, 'total responsabilidad')
    ;   sub_atom(Texto, _, _, _, 'penalidad resarcitoria')
    ),
    (   sub_atom(Texto, _, _, _, '$10,000')
    ;   sub_atom(Texto, _, _, _, 'compensar dicho monto')
    ;   sub_atom(Texto, _, _, _, 'saldos pendientes de pago')
    ).

clausula_riesgosa(Id, general, alto) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'irrenunciable'),
    sub_atom(Texto, _, _, _, 'renuncia').

clausula_riesgosa(Id, general, alto) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'sin contraprestacion'),
    (   sub_atom(Texto, _, _, _, 'exclusividad')
    ;   sub_atom(Texto, _, _, _, 'cesion')
    ).

clausula_riesgosa(Id, general, alto) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'sin limite'),
    (   sub_atom(Texto, _, _, _, 'responsabilidad')
    ;   sub_atom(Texto, _, _, _, 'penalidad')
    ;   sub_atom(Texto, _, _, _, 'obligacion')
    ).

clausula_riesgosa(Id, general, critico) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'renuncia a acciones').

clausula_riesgosa(Id, general, critico) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'no podra cuestionar').

clausula_riesgosa(Id, general, alto) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'se entendera aceptado automaticamente').

clausula_riesgosa(Id, general, medio) :-
    clausula(Id, _, Texto),
    sub_atom(Texto, _, _, _, 'sin detallar procedimiento'),
    atom_length(Texto, Len),
    Len > 40.
