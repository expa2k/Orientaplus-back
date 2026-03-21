def calcular_vector_riasec(respuestas_con_dimension):
    sumas = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    conteos = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}

    for dimension, valor in respuestas_con_dimension:
        dim = dimension.upper()
        if dim in sumas:
            sumas[dim] += int(valor)
            conteos[dim] += 1

    vector = {}
    for dim in 'RIASEC':
        if conteos[dim] > 0:
            vector[dim] = round(sumas[dim] / conteos[dim], 2)
        else:
            vector[dim] = 0.0

    return vector


def obtener_dimensiones_ambiguas(vector_riasec, umbral=0.5):
    if not vector_riasec:
        return []

    scores = [(dim, score) for dim, score in vector_riasec.items() if score > 0]
    if len(scores) < 2:
        return []

    scores.sort(key=lambda x: x[1], reverse=True)
    top_score = scores[0][1]

    ambiguas = []
    for dim, score in scores[1:]:
        if (top_score - score) <= umbral:
            ambiguas.append(dim)

    if ambiguas:
        ambiguas.insert(0, scores[0][0])

    return ambiguas


def decidir_siguiente_bloque(vector_riasec, bloque_actual, total_bloques=3):
    if not vector_riasec:
        return {'accion': 'continuar', 'siguiente_bloque': bloque_actual + 1, 'dimensiones_foco': [], 'perfil_claro': False}

    if bloque_actual == 1:
        # Fase Exploratoria terminada -> Filtrar a las mejores 3 familias de carreras
        top_3_tuplas = obtener_top_dimensiones(vector_riasec, n=3)
        top_3 = [dim for dim, score in top_3_tuplas]
        
        return {
            'accion': 'continuar',
            'siguiente_bloque': 2,
            'dimensiones_foco': top_3,
            'perfil_claro': False
        }
        
    elif bloque_actual == 2:
        # Fase de Descubrimiento terminada -> Batalla cara a cara entre las TOP 2
        top_2_tuplas = obtener_top_dimensiones(vector_riasec, n=2)
        top_2 = [dim for dim, score in top_2_tuplas]
        
        return {
            'accion': 'continuar',
            'siguiente_bloque': 3,
            'dimensiones_foco': top_2,
            'perfil_claro': False
        }

    return {
        'accion': 'finalizar',
        'siguiente_bloque': None,
        'dimensiones_foco': [],
        'perfil_claro': True
    }


def obtener_top_dimensiones(vector_riasec, n=3):
    scores = [(dim, score) for dim, score in vector_riasec.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]


def calcular_afinidad_carrera(vector_estudiante, perfil_carrera):
    if not perfil_carrera or not vector_estudiante:
        return 0.0

    max_posible = len(perfil_carrera) * 5.0
    score_total = 0.0

    for i, dim in enumerate(perfil_carrera):
        peso = len(perfil_carrera) - i
        score_dim = vector_estudiante.get(dim, 0)
        score_total += score_dim * peso

    max_ponderado = sum((len(perfil_carrera) - i) * 5 for i in range(len(perfil_carrera)))

    if max_ponderado == 0:
        return 0.0

    afinidad_bruta = (score_total / max_ponderado) * 100
    
    # "Disfrazar de bonito": Mapeamos la afinidad cruda (que suele estar entre 30% y 60%)
    # a la escala visual atractiva de 75% a 98%, conservando la distancia matemática real.
    afinidad = 75.0 + (afinidad_bruta / 60.0) * 23.0
    afinidad = min(afinidad, 99.9)
    
    return round(afinidad, 1)
