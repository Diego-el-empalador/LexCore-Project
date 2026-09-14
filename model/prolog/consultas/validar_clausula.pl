:- set_prolog_flag(encoding, utf8).

% validar/2 - valida una clausula individual
% Uso: validar(+Id, -Resultado)
validar(Id, riesgo(Tipo, Severidad)) :-
    clausula_riesgosa(Id, Tipo, Severidad), !.
validar(Id, valida) :-
    clausula(Id, _, _).

% articulo_violado/3 - retorna el articulo del CC que viola la clausula
% Uso: articulo_violado(+Id, -Codigo, -Descripcion)
articulo_violado(Id, Codigo, Descripcion) :-
    clausula_riesgosa(Id, _, _),
    clausula(Id, Tipo, _),
    articulo_cc(Codigo, Descripcion, Tipo).
