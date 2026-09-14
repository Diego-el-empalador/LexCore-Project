:- set_prolog_flag(encoding, utf8).

% verificar_contrato/1 - estado global
verificar_contrato(aprobado) :-
    contrato_valido, !.
verificar_contrato(con_riesgos).

% reporte_clausula/4 - reporte detallado con articulo del CC
reporte_clausula(Id, TipoRiesgo, Severidad, ArticuloCC) :-
    clausula_riesgosa(Id, TipoRiesgo, Severidad),
    clausula(Id, TipoClausula, _),
    (   articulo_cc(ArticuloCC, _, TipoClausula)
    ->  true
    ;   ArticuloCC = 'Art. 1354 CC'
    ).

% reporte_completo/4
reporte_completo(Dictamen, Score, Total, Riesgosas) :-
    dictamen_contrato(Dictamen),
    score_contrato(Score),
    resumen_contrato(Total, Riesgosas).

% cadena_razonamiento/3 - explica el riesgo de una clausula
cadena_razonamiento(Id, DescripcionPatron, ArticuloCC) :-
    clausula_riesgosa(Id, TipoRiesgo, Severidad),
    clausula(Id, TipoClausula, _),
    (   patron_riesgo(TipoRiesgo, DescripcionPatron)
    ->  true
    ;   patron_riesgo(clausula_vaga, DescripcionPatron)
    ),
    (   articulo_cc(ArticuloCC, _, TipoClausula)
    ->  true
    ;   (   Severidad = critico
        ->  ArticuloCC = 'Art. 1398 CC'
        ;   ArticuloCC = 'Art. 1354 CC'
        )
    ).
