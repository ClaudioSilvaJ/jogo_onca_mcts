from collections import deque
import sys

from tabuleiro import tabuleiro_conecta, tabuleiro_recebe, tabuleiro_envia
from fun_auxiliares import gerar_hash_tabuleiro, formatar_comando_movimento, contar_caes, onca_sem_movimentos
from mct_onca import escolher_movimento_seguro

HISTORICO_MAXIMO = 16

def interpretar_jogada(texto_jogada):
    if not texto_jogada:
        return None

    tokens = texto_jogada.strip().split()
    if len(tokens) < 2:
        return None

    tipo = tokens[1]

    if tipo == "m" and len(tokens) >= 6:
        origem_l, origem_c, destino_l, destino_c = map(int, tokens[2:6])
        return "m", (origem_l, origem_c, destino_l, destino_c)

    if tipo == "s" and len(tokens) >= 5:
        num_saltos = int(tokens[2])
        coordenadas = list(map(int, tokens[3 : 3 + (2 * (num_saltos + 1))]))
        return "s", tuple(coordenadas)

    return None


def interpretar_comunicacao_recebida(buffer):
    linhas = [linha.rstrip("\r") for linha in buffer.split("\n")]
    linhas = [linha for linha in linhas if linha.strip()]

    lado_header = None
    jogada = ""
    linhas_tabuleiro = []

    for linha in linhas:
        s = linha.strip()
        if not s:
            continue

        if s in ("o", "c") and lado_header is None:
            lado_header = s
            continue
        if (s.startswith("o ") or s.startswith("c ")) and not jogada:
            jogada = s
            continue
        if s.startswith("#"):
            linhas_tabuleiro.append(s)

    lado_from_jogada = None
    if jogada:
        lado_previo = jogada[0]
        if lado_previo == "o":
            lado_from_jogada = "c"
        elif lado_previo == "c":
            lado_from_jogada = "o"

    if lado_from_jogada is not None:
        lado_turno = lado_from_jogada
    elif lado_header is not None:
        lado_turno = lado_header
    else:
        lado_turno = "?"

    tabuleiro = [["#"] * 6 for _ in range(8)]

    if linhas_tabuleiro:
        if len(linhas_tabuleiro) > 9:
            linhas_tabuleiro = linhas_tabuleiro[-9:]
        for indice, linha in enumerate(linhas_tabuleiro[1:8], 1):
            for coluna in range(1, 6):
                tabuleiro[indice][coluna] = linha[coluna]

    return lado_turno, jogada, tabuleiro



def detectar_vencedor(tabuleiro):
    num_caes = contar_caes(tabuleiro)
    if num_caes <= 9:
        return "o"
    if onca_sem_movimentos(tabuleiro):
        return "c"

    return None



def ler_parametros_linha_comando(argv):
    lado_jogador = argv[1][0]
    endereco_ip = argv[2] if len(argv) > 2 else "127.0.0.1"
    porta_servidor = int(argv[3]) if len(argv) > 3 else 10001
    simulacoes_monte_carlo = int(argv[4]) if len(argv) > 4 else 120
    largura_beam = int(argv[5]) if len(argv) > 5 else 6

    return lado_jogador, endereco_ip, porta_servidor, simulacoes_monte_carlo, largura_beam


def main():
    lado_jogador, endereco_ip, porta_servidor, simulacoes_monte_carlo, largura_beam = ler_parametros_linha_comando(sys.argv)
    historico_posicoes = deque(maxlen=HISTORICO_MAXIMO)
    args_conexao = [sys.argv[0], lado_jogador, endereco_ip, str(porta_servidor)]
    tabuleiro_conecta(len(args_conexao), args_conexao)
    while True:
        comunicacao_recebida = tabuleiro_recebe()
        if not comunicacao_recebida:
            continue

        lado_turno, texto_jogada_anterior, tabuleiro_atual = interpretar_comunicacao_recebida(comunicacao_recebida)

        vencedor = detectar_vencedor(tabuleiro_atual)
        if vencedor is not None:
            print("\nPartida encerrada")
            break
        
        hash_atual = gerar_hash_tabuleiro(tabuleiro_atual)
        historico_posicoes.append(hash_atual)
        jogada_anterior_interpretada = interpretar_jogada(texto_jogada_anterior)

        if lado_turno != lado_jogador:
            print(comunicacao_recebida)
            continue

        print("\nAnalisando posição (MCTS)")
        movimento_escolhido = escolher_movimento_seguro(
            tabuleiro_atual,
            lado_jogador,
            historico_posicoes,
            jogada_anterior_interpretada,
            simulacoes_monte_carlo,
            largura_beam,
        )

        if not movimento_escolhido:
            print("Nenhum movimento válido encontrado.")
            tabuleiro_envia("n\n")
            continue

        comando = formatar_comando_movimento(lado_jogador, movimento_escolhido)
        print(f"Movimento escolhido: {comando.strip()}")
        tabuleiro_envia(comando)


if __name__ == "__main__":
    main()
