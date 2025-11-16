from functools import lru_cache
from controlador import pos_valida, mov_possivel

JANELA_AVALIACAO_HISTORICO = 6
PENALIDADE_LOOP = 9_999
VIZINHOS_MOVIMENTO = {}
VIZINHOS_SALTO = {}

POSICOES_VALIDAS = {
    (linha, coluna)
    for linha in range(1, 8)
    for coluna in range(1, 6)
    if pos_valida(linha, coluna)
}

@lru_cache(maxsize=None)
def movimento_possivel(tipo_movimento, linha_origem, coluna_origem, linha_destino, coluna_destino):
    return mov_possivel(tipo_movimento, linha_origem, coluna_origem, linha_destino, coluna_destino)

for linha, coluna in POSICOES_VALIDAS:
    movimentos_simples = []
    saltos_possiveis = []

    for destino_linha, destino_coluna in POSICOES_VALIDAS:
        if movimento_possivel("m", linha, coluna, destino_linha, destino_coluna):
            movimentos_simples.append((destino_linha, destino_coluna))
        if movimento_possivel("s", linha, coluna, destino_linha, destino_coluna):
            saltos_possiveis.append((destino_linha, destino_coluna))

    VIZINHOS_MOVIMENTO[(linha, coluna)] = movimentos_simples
    VIZINHOS_SALTO[(linha, coluna)] = saltos_possiveis


def copia_tabuleiro(tabuleiro):
    return [linha[:] for linha in tabuleiro]


def contar_caes(tabuleiro):
    return sum(celula == "c" for linha in tabuleiro for celula in linha)


def encontrar_onca(tabuleiro):
    for linha in range(1, 8):
        for coluna in range(1, 6):
            if tabuleiro[linha][coluna] == "o":
                return linha, coluna
    return -1, -1


def posicao_valida(linha, coluna):
    return pos_valida(linha, coluna)


def gerar_hash_tabuleiro(tabuleiro):
    return "".join("".join(tabuleiro[i][1:6]) for i in range(1, 8))


def eh_movimento_reverso(jogada_anterior, jogada_atual):
    if not jogada_anterior or not jogada_atual:
        return False
    if jogada_anterior[0] != "m" or jogada_atual[0] != "m":
        return False

    origem_l_ant, origem_c_ant, destino_l_ant, destino_c_ant = jogada_anterior[1]
    origem_l_atu, origem_c_atu, destino_l_atu, destino_c_atu = jogada_atual[1]

    return (origem_l_atu, origem_c_atu, destino_l_atu, destino_c_atu) == (
        destino_l_ant,
        destino_c_ant,
        origem_l_ant,
        origem_c_ant,
    )

def validar_movimento(tabuleiro, jogador, movimento):
    if not movimento:
        return False

    tipo, dados = movimento

    if tipo == "m":
        origem_l, origem_c, destino_l, destino_c = dados
        if not (posicao_valida(origem_l, origem_c) and posicao_valida(destino_l, destino_c)):
            return False
        if tabuleiro[origem_l][origem_c] != jogador:
            return False
        if tabuleiro[destino_l][destino_c] != "-":
            return False
        if not movimento_possivel("m", origem_l, origem_c, destino_l, destino_c):
            return False
        return True

    if tipo == "s":
        if jogador != "o":
            return False

        coordenadas = list(dados)
        if len(coordenadas) < 4:
            return False

        linha_onca, coluna_onca = encontrar_onca(tabuleiro)
        if (coordenadas[0], coordenadas[1]) != (linha_onca, coluna_onca):
            return False

        tabuleiro_temp = copia_tabuleiro(tabuleiro)
        linha_atual, coluna_atual = coordenadas[0], coordenadas[1]

        for indice in range(0, len(coordenadas) - 2, 2):
            linha_destino = coordenadas[indice + 2]
            coluna_destino = coordenadas[indice + 3]

            if not movimento_possivel("s", linha_atual, coluna_atual, linha_destino, coluna_destino):
                return False
            if not posicao_valida(linha_destino, coluna_destino):
                return False
            if tabuleiro_temp[linha_destino][coluna_destino] != "-":
                return False

            linha_meio = (linha_atual + linha_destino) // 2
            coluna_meio = (coluna_atual + coluna_destino) // 2
            if not posicao_valida(linha_meio, coluna_meio):
                return False
            if tabuleiro_temp[linha_meio][coluna_meio] != "c":
                return False

            tabuleiro_temp[linha_atual][coluna_atual] = "-"
            tabuleiro_temp[linha_meio][coluna_meio] = "-"
            tabuleiro_temp[linha_destino][coluna_destino] = "o"
            linha_atual, coluna_atual = linha_destino, coluna_destino

        return True

    return False

def formatar_comando_movimento(jogador, movimento):
    tipo, dados = movimento
    if tipo == "m":
        origem_l, origem_c, destino_l, destino_c = dados
        return f"{jogador} m {origem_l} {origem_c} {destino_l} {destino_c}\n"

    coordenadas = list(dados)
    num_saltos = len(coordenadas) // 2 - 1
    coords_texto = " ".join(str(x) for x in coordenadas)
    return f"{jogador} s {num_saltos} {coords_texto}\n"

def onca_sem_movimentos(tabuleiro):
    linha_onca, coluna_onca = encontrar_onca(tabuleiro)
    if linha_onca == -1 or coluna_onca == -1:
        return True
    for ld, cd in VIZINHOS_MOVIMENTO.get((linha_onca, coluna_onca), []):
        if tabuleiro[ld][cd] == "-":
            return False
    for ld, cd in VIZINHOS_SALTO.get((linha_onca, coluna_onca), []):
        if tabuleiro[ld][cd] != "-":
            continue

        lm = (linha_onca + ld) // 2
        cm = (coluna_onca + cd) // 2
        if posicao_valida(lm, cm) and tabuleiro[lm][cm] == "c":
            return False
    return True
