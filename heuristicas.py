from fun_auxiliares import (
    encontrar_onca,
    posicao_valida,
    VIZINHOS_MOVIMENTO,
    VIZINHOS_SALTO,
)


def calcular_liberdade_onca(tabuleiro):
    linha_onca, coluna_onca = encontrar_onca(tabuleiro)
    casas_livres = 0

    for linha_vizinha, coluna_vizinha in VIZINHOS_MOVIMENTO.get((linha_onca, coluna_onca), []):
        if tabuleiro[linha_vizinha][coluna_vizinha] == "-":
            casas_livres += 1

    return casas_livres


def contar_caes_capturaveis(tabuleiro):
    linha_onca, coluna_onca = encontrar_onca(tabuleiro)
    capturas_possiveis = 0

    for linha_destino, coluna_destino in VIZINHOS_SALTO.get((linha_onca, coluna_onca), []):
        linha_meio = (linha_onca + linha_destino) // 2
        coluna_meio = (coluna_onca + coluna_destino) // 2

        if (
            tabuleiro[linha_destino][coluna_destino] == "-"
            and tabuleiro[linha_meio][coluna_meio] == "c"
        ):
            capturas_possiveis += 1

    return capturas_possiveis


def calcular_cerco(tabuleiro):
    linha_onca, coluna_onca = encontrar_onca(tabuleiro)
    pontos_cerco = 0

    for linha_viz, coluna_viz in VIZINHOS_MOVIMENTO.get((linha_onca, coluna_onca), []):
        if (
            abs(linha_onca - linha_viz) <= 1
            and abs(coluna_onca - coluna_viz) <= 1
            and (linha_onca != linha_viz or coluna_onca != coluna_viz)
        ):
            if tabuleiro[linha_viz][coluna_viz] == "c":
                pontos_cerco += 4

    for delta_linha in (-2, 0, 2):
        for delta_coluna in (-2, 0, 2):
            if delta_linha == 0 and delta_coluna == 0:
                continue
            linha_anel = linha_onca + delta_linha
            coluna_anel = coluna_onca + delta_coluna
            if posicao_valida(linha_anel, coluna_anel) and tabuleiro[linha_anel][coluna_anel] == "c":
                pontos_cerco += 2

    return pontos_cerco