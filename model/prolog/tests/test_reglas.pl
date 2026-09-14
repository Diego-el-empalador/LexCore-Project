:- set_prolog_flag(encoding, utf8).
:- use_module(library(plunit)).
:- use_module(library(aggregate)).

:- consult('base_conocimiento/hechos').
:- consult('base_conocimiento/reglas_generales').
:- consult('base_conocimiento/reglas_civiles').
:- consult('base_conocimiento/reglas_laborales').
:- consult('base_conocimiento/reglas_comerciales').
:- consult('consultas/validar_clausula').
:- consult('consultas/detectar_riesgo').
:- consult('consultas/verificar_contrato').

% Helper: inserta y luego limpia la clausula de prueba
limpiar(Id) :-
    (retract(user:clausula(Id, _, _)) -> true ; true).


:- begin_tests(reglas_generales).

test(g1_penalidad_es_alto) :-
    assert(user:clausula(1, penalidad, 'Se aplicara multa por incumplimiento')),
    clausula_riesgosa(1, penalidad, alto),
    limpiar(1).

test(g2_interes_compuesto_critico) :-
    assert(user:clausula(2, penalidad, 'Se aplicara interes compuesto mensual')),
    clausula_riesgosa(2, penalidad, critico),
    limpiar(2).

test(g4_plazo_sin_unidad_medio) :-
    assert(user:clausula(3, plazo, 'El contrato sera por un tiempo razonable segun criterio')),
    clausula_riesgosa(3, plazo, medio),
    limpiar(3).

test(g4_plazo_con_dias_no_medio, [fail]) :-
    assert(user:clausula(4, plazo, 'El contrato durara 30 dias calendario exactos')),
    clausula_riesgosa(4, plazo, medio),
    limpiar(4).

test(g5_rescision_sin_preaviso_alto) :-
    assert(user:clausula(5, rescision, 'Cualquiera puede terminar el contrato libremente')),
    clausula_riesgosa(5, rescision, alto),
    limpiar(5).

test(g6_clausula_general_corta_bajo) :-
    assert(user:clausula(6, general, 'Ver anexo')),
    clausula_riesgosa(6, general, bajo),
    limpiar(6).

test(g7_exoneracion_critico) :-
    assert(user:clausula(7, general, 'La empresa no sera responsable por danos causados')),
    clausula_riesgosa(7, general, critico),
    limpiar(7).

test(contrato_vacio_es_valido) :-
    contrato_valido.

:- end_tests(reglas_generales).

:- begin_tests(reglas_laborales).

test(l1_horas_extras_critico) :-
    assert(user:clausula(10, obligacion, 'El empleado realizara horas extras sin pago')),
    clausula_riesgosa(10, obligacion, critico),
    limpiar(10).

test(l2_indefinido_sin_preaviso_alto) :-
    assert(user:clausula(11, plazo, 'El contrato es de duracion indefinida sin clausulas adicionales')),
    clausula_riesgosa(11, plazo, alto),
    limpiar(11).

test(l2_indefinido_con_preaviso_no_alto, [fail]) :-
    assert(user:clausula(12, plazo, 'El contrato es indefinido con preaviso de 30 dias obligatorio')),
    clausula_riesgosa(12, plazo, alto),
    limpiar(12).

test(l5_renuncia_beneficios_critico) :-
    assert(user:clausula(13, obligacion, 'Trabajador acepta sin beneficios laborales de ley')),
    clausula_riesgosa(13, obligacion, critico),
    limpiar(13).

:- end_tests(reglas_laborales).

:- begin_tests(reglas_civiles).

test(c2_rescision_sin_garantias_alto) :-
    assert(user:clausula(20, rescision, 'El arrendador puede resolver el contrato en cualquier momento')),
    clausula_riesgosa(20, rescision, alto),
    limpiar(20).

test(c6_confidencialidad_sin_plazo_alto) :-
    assert(user:clausula(21, confidencialidad, 'El receptor se obliga a guardar confidencialidad total')),
    clausula_riesgosa(21, confidencialidad, alto),
    limpiar(21).

:- end_tests(reglas_civiles).

:- begin_tests(reglas_comerciales).

test(m5_cesion_datos_critico) :-
    assert(user:clausula(30, confidencialidad, 'La empresa puede ceder la informacion a terceros aliados')),
    clausula_riesgosa(30, confidencialidad, critico),
    limpiar(30).

:- end_tests(reglas_comerciales).

:- begin_tests(dictamen).

test(dictamen_alto_con_critico) :-
    assert(user:clausula(40, penalidad, 'Multa con interes compuesto sin limite alguno')),
    dictamen_contrato('ALTO'),
    limpiar(40).

test(score_100_sin_clausulas) :-
    retractall(user:clausula(_, _, _)),
    score_contrato(100).

test(score_menor_100_con_riesgo) :-
    assert(user:clausula(50, penalidad, 'Multa por incumplimiento de contrato firmado')),
    score_contrato(Score),
    Score < 100,
    limpiar(50).

test(reporte_completo_funciona) :-
    assert(user:clausula(60, general, 'Ver')),
    reporte_completo(_, Score, Total, _),
    Score >= 0, Score =< 100,
    Total >= 1,
    limpiar(60).

:- end_tests(dictamen).