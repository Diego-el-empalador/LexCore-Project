:- set_prolog_flag(encoding, utf8).

:- multifile clausula_riesgosa/3.

:- dynamic clausula/3.

tipo_clausula(obligacion).
tipo_clausula(plazo).
tipo_clausula(penalidad).
tipo_clausula(confidencialidad).
tipo_clausula(rescision).
tipo_clausula(no_competencia).
tipo_clausula(propiedad_intelectual).
tipo_clausula(datos_personales).
tipo_clausula(arbitraje).
tipo_clausula(modificacion_unilateral).
tipo_clausula(general).

nivel_riesgo(bajo,    1).
nivel_riesgo(medio,   2).
nivel_riesgo(alto,    3).
nivel_riesgo(critico, 4).

articulo_cc('Art. 1354 CC',
    'Libertad contractual limitada por norma imperativa',
    general).

articulo_cc('Art. 1355 CC',
    'El Estado puede imponer reglas por interes social o etico',
    general).

articulo_cc('Art. 1397 CC',
    'Clausulas en contratos no negociados se interpretan contra el redactor',
    general).

articulo_cc('Art. 1398 CC',
    'Nulas las clausulas que exoneran responsabilidad del redactor en contratos por adhesion',
    general).

articulo_cc('Art. 1399 CC',
    'Nulas las estipulaciones contrarias a reglas de contratos nominados por adhesion',
    general).

articulo_cc('Art. 1400 CC',
    'Abusivas las clausulas que causan desequilibrio importante contra la parte debil',
    general).

articulo_cc('Art. 1341 CC',
    'La penalidad limita el resarcimiento; puede ser revisada por el juez',
    penalidad).

articulo_cc('Art. 1346 CC',
    'El juez puede reducir penalidad manifiestamente excesiva',
    penalidad).

articulo_cc('Art. 1243 CC',
    'Tasa maxima de interes fijada por BCR; todo exceso se devuelve',
    penalidad).

articulo_cc('Art. 1370 CC',
    'La rescision deja sin efecto el contrato por causal al momento de su celebracion',
    rescision).

articulo_cc('Art. 1371 CC',
    'La resolucion deja sin efecto el contrato por causal sobreviniente',
    rescision).

articulo_cc('Art. 1374 CC',
    'Notificacion recepticia: efectos desde que llega al destinatario',
    rescision).

articulo_cc('Art. 1238 CC',
    'El plazo debe ser determinado o determinable',
    plazo).

articulo_cc('Art. 1240 CC',
    'Sin plazo designado, el acreedor puede exigir pago inmediato',
    plazo).

articulo_cc('Art. 1402 CC',
    'El objeto del contrato no puede ser prestacion imposible',
    obligacion).

articulo_cc('Art. 1403 CC',
    'La promesa sobre bienes futuros esta sujeta a que lleguen a existir',
    obligacion).

articulo_cc('Art. 1405 CC',
    'Nulo todo contrato sobre herencia de persona viva',
    obligacion).

articulo_cc('Art. 1362 CC',
    'Contratos deben ejecutarse segun reglas de buena fe',
    confidencialidad).

articulo_cc('Art. 1378 CC',
    'Los pactos deben precisar su alcance y temporalidad',
    confidencialidad).

articulo_cc('Ley 29733',
    'El tratamiento de datos personales requiere consentimiento, finalidad y proporcionalidad',
    datos_personales).

articulo_cc('D. Leg. 822',
    'La cesion de derechos de propiedad intelectual debe ser expresa y delimitada',
    propiedad_intelectual).

articulo_cc('D. Leg. 1071',
    'El arbitraje debe respetar debido proceso y equilibrio entre las partes',
    arbitraje).

articulo_cc('Art. 1400 CC',
    'Son abusivas las clausulas que generan desequilibrio importante contra la parte debil',
    no_competencia).

articulo_cc('Art. 1354 CC',
    'La autonomia privada no ampara modificaciones unilaterales abusivas',
    modificacion_unilateral).

patron_riesgo(penalidad,
    'Penalidad potencialmente excesiva sin tope definido').

patron_riesgo(penalidad_excesiva,
    'Penalidad con interes compuesto puede superar maximo legal del BCR').

patron_riesgo(plazo,
    'Plazo indeterminado: no expresa dias, meses ni anios').

patron_riesgo(rescision,
    'Rescision sin preaviso ni forma de notificacion: desampara a la parte debil').

patron_riesgo(obligacion,
    'Obligacion potencialmente imposible, ilegal o que viola derechos irrenunciables').

patron_riesgo(clausula_leonina,
    'Clausula que favorece unilateralmente a una sola parte').

patron_riesgo(confidencialidad,
    'Confidencialidad sin plazo de vigencia: podria ser perpetua e inaplicable').

patron_riesgo(no_competencia,
    'No competencia excesiva en tiempo, territorio o sin compensacion').

patron_riesgo(propiedad_intelectual,
    'Cesion amplia de derechos de propiedad intelectual sin limites claros').

patron_riesgo(datos_personales,
    'Tratamiento o transferencia de datos personales sin consentimiento ni finalidad legitima').

patron_riesgo(arbitraje,
    'Arbitraje impuesto de forma obligatoria o designado unilateralmente').

patron_riesgo(modificacion_unilateral,
    'Una sola parte puede cambiar el contrato sin negociacion ni aviso razonable').

patron_riesgo(general,
    'Clausula vaga, exoneratoria o con desequilibrio contractual').

patron_riesgo(clausula_vaga,
    'Clausula demasiado corta o vaga para tener efecto juridico real').
