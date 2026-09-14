:- set_prolog_flag(encoding, utf8).

% riesgos_contrato/1 - colecta todos los hallazgos (sin duplicados)
riesgos_contrato(Hallazgos) :-
    findall(
        hallazgo(Id, Tipo, Severidad),
        clausula_riesgosa(Id, Tipo, Severidad),
        HallazgosDup
    ),
    sort(HallazgosDup, Hallazgos).

% contar_por_severidad/2
contar_por_severidad(Severidad, Cantidad) :-
    aggregate_all(count, clausula_riesgosa(_, _, Severidad), Cantidad).

% dictamen_contrato/1 - ALTO | MEDIO | BAJO
% ALTO  : hay clausula critica, o 2+ clausulas altas
% MEDIO : 1 clausula alta, o 2+ medias
% BAJO  : solo bajas o medias aisladas, o ninguna
dictamen_contrato('ALTO') :-
    clausula_riesgosa(_, _, critico), !.

dictamen_contrato('ALTO') :-
    contar_por_severidad(alto, N),
    N >= 2, !.

dictamen_contrato('MEDIO') :-
    clausula_riesgosa(_, _, alto), !.

dictamen_contrato('MEDIO') :-
    contar_por_severidad(medio, N),
    N >= 2, !.

dictamen_contrato('BAJO') :-
    (clausula_riesgosa(_, _, medio) ; clausula_riesgosa(_, _, bajo)), !.

dictamen_contrato('BAJO') :-
    \+ clausula_riesgosa(_, _, _).

% score_contrato/1 - puntaje de seguridad 0 a 100
% Formula: 100 - Criticos*30 - Altos*15 - Medios*8 - Bajos*3
score_contrato(Score) :-
    contar_por_severidad(critico, C),
    contar_por_severidad(alto,    A),
    contar_por_severidad(medio,   M),
    contar_por_severidad(bajo,    B),
    Raw is 100 - (C * 30) - (A * 15) - (M * 8) - (B * 3),
    Score is max(0, Raw).

% resumen_contrato/2 - total clausulas y cuantas son riesgosas (IDs unicos)
resumen_contrato(Total, Riesgosos) :-
    aggregate_all(count, clausula(_, _, _), Total),
    findall(Id, clausula_riesgosa(Id, _, _), Ids),
    sort(Ids, IdsUnicos),
    length(IdsUnicos, Riesgosos).
