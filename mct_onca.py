import random
import math

from fun_auxiliares import (
    VIZINHOS_MOVIMENTO,
    VIZINHOS_SALTO,
    copia_tabuleiro,
    encontrar_onca,
    gerar_hash_tabuleiro,
    eh_movimento_reverso,
    validar_movimento,
)
from heuristicas import calcular_liberdade_onca, contar_caes_capturaveis, calcular_cerco

class NoMCTS:
    def __init__(self, tabuleiro, jogador_atual, jogada_anterior, movimento=None, pai=None):
        self.tabuleiro = tabuleiro
        self.jogador_atual = jogador_atual
        self.jogada_anterior = jogada_anterior
        self.movimento = movimento
        self.pai = pai

        self.filhos = []
        self.movimentos_nao_expandidos = None
        self.visitas = 0
        self.vitorias = 0.0


class MCTSOnca:
    def __init__(self, simulacoes_por_movimento=120, largura_beam=6, max_turnos_sim=40, c_param=1.4):
        self.simulacoes_por_movimento = max(1, simulacoes_por_movimento)
        self.largura_beam = max(1, largura_beam)
        self.max_turnos_sim = max_turnos_sim
        self.c_param = c_param

    def gerar_movimentos_onca(self, tabuleiro):
        linha_onca, coluna_onca = encontrar_onca(tabuleiro)
        sequencias_salto = []

        def buscar_saltos(linha_atual, coluna_atual, tabuleiro_atual, caminho):
            encontrou_salto = False

            for linha_destino, coluna_destino in VIZINHOS_SALTO.get((linha_atual, coluna_atual), []):
                linha_meio = (linha_atual + linha_destino) // 2
                coluna_meio = (coluna_atual + coluna_destino) // 2

                if (
                    tabuleiro_atual[linha_meio][coluna_meio] != "c"
                    or tabuleiro_atual[linha_destino][coluna_destino] != "-"
                ):
                    continue

                tabuleiro_novo = copia_tabuleiro(tabuleiro_atual)
                tabuleiro_novo[linha_atual][coluna_atual] = "-"
                tabuleiro_novo[linha_meio][coluna_meio] = "-"
                tabuleiro_novo[linha_destino][coluna_destino] = "o"

                encontrou_salto = True
                buscar_saltos(
                    linha_destino,
                    coluna_destino,
                    tabuleiro_novo,
                    caminho + [(linha_destino, coluna_destino)],
                )

            if not encontrou_salto and len(caminho) > 1:
                coordenadas = tuple(coord for pos in caminho for coord in pos)
                sequencias_salto.append(coordenadas)

        buscar_saltos(linha_onca, coluna_onca, tabuleiro, [(linha_onca, coluna_onca)])

        movimentos_simples = []
        for linha_destino, coluna_destino in VIZINHOS_MOVIMENTO.get((linha_onca, coluna_onca), []):
            if tabuleiro[linha_destino][coluna_destino] == "-":
                movimentos_simples.append(
                    ("m", (linha_onca, coluna_onca, linha_destino, coluna_destino))
                )

        return [("s", sequencia) for sequencia in sequencias_salto] + movimentos_simples

    def gerar_movimentos_caes(self, tabuleiro):
        movimentos = []

        for linha in range(1, 8):
            for coluna in range(1, 6):
                if tabuleiro[linha][coluna] != "c":
                    continue

                for linha_destino, coluna_destino in VIZINHOS_MOVIMENTO.get((linha, coluna), []):
                    if tabuleiro[linha_destino][coluna_destino] == "-":
                        movimentos.append(("m", (linha, coluna, linha_destino, coluna_destino)))

        random.shuffle(movimentos)
        return movimentos

    def realiza_sequencia_saltos(self, tabuleiro, coordenadas):
        tabuleiro_novo = copia_tabuleiro(tabuleiro)

        for indice in range(0, len(coordenadas) - 2, 2):
            linha_origem = coordenadas[indice]
            coluna_origem = coordenadas[indice + 1]
            linha_destino = coordenadas[indice + 2]
            coluna_destino = coordenadas[indice + 3]

            tabuleiro_novo[linha_origem][coluna_origem] = "-"
            tabuleiro_novo[
                (linha_origem + linha_destino) // 2
            ][(coluna_origem + coluna_destino) // 2] = "-"
            tabuleiro_novo[linha_destino][coluna_destino] = "o"

        return tabuleiro_novo

    def realiza_movimento(self, tabuleiro, jogador, movimento):
        tipo, dados = movimento

        if tipo == "m":
            origem_l, origem_c, destino_l, destino_c = dados
            tabuleiro_novo = copia_tabuleiro(tabuleiro)
            tabuleiro_novo[origem_l][origem_c] = "-"
            tabuleiro_novo[destino_l][destino_c] = jogador
            return tabuleiro_novo
        return self.realiza_sequencia_saltos(tabuleiro, list(dados))

    def simular_jogo_aleatorio(self, tabuleiro, jogador_inicial, max_turnos=40, jogada_anterior=None):
        jogador_atual = jogador_inicial

        for _ in range(max_turnos):
            gerador_movimentos = (
                self.gerar_movimentos_onca if jogador_atual == "o" else self.gerar_movimentos_caes
            )
            movimentos = gerador_movimentos(tabuleiro)

            movimentos = [m for m in movimentos if not eh_movimento_reverso(jogada_anterior, m)]

            if not movimentos:
                return "c" if jogador_atual == "o" else "o"

            if jogador_atual == "c":
                melhor_movimento = None
                melhor_chave = (999, 999, 999)
                amostra = movimentos if len(movimentos) <= 6 else random.sample(movimentos, 6)

                for movimento in amostra:
                    if not validar_movimento(tabuleiro, "c", movimento):
                        continue

                    tabuleiro_teste = self.realiza_movimento(tabuleiro, "c", movimento)
                    liberdade = calcular_liberdade_onca(tabuleiro_teste)
                    capturaveis = contar_caes_capturaveis(tabuleiro_teste)
                    cerco = calcular_cerco(tabuleiro_teste)
                    chave = (liberdade, capturaveis, -cerco)

                    if chave < melhor_chave:
                        melhor_chave = chave
                        melhor_movimento = movimento

                if melhor_movimento:
                    tipo, dados = melhor_movimento
                else:
                    tipo, dados = random.choice(movimentos)
            else:
                tipo, dados = random.choice(movimentos)

            if not validar_movimento(tabuleiro, jogador_atual, (tipo, dados)):
                jogada_anterior = None
                continue

            tabuleiro = self.realiza_movimento(tabuleiro, jogador_atual, (tipo, dados))
            jogada_anterior = (tipo, dados)
            jogador_atual = "c" if jogador_atual == "o" else "o"

        return "empate"

    def gerar_movimentos_legais(self, tabuleiro, jogador, jogada_anterior, largura_beam=None):
        if largura_beam is None:
            largura_beam = self.largura_beam

        gerador = self.gerar_movimentos_onca if jogador == "o" else self.gerar_movimentos_caes
        movimentos_brutos = gerador(tabuleiro)

        movimentos = []
        for movimento in movimentos_brutos:
            if eh_movimento_reverso(jogada_anterior, movimento):
                continue
            if not validar_movimento(tabuleiro, jogador, movimento):
                continue
            movimentos.append(movimento)

        if largura_beam is not None and largura_beam > 0 and len(movimentos) > largura_beam:
            movimentos = random.sample(movimentos, largura_beam)

        return movimentos

    def _ucb1(self, filho, total_visitas_pai):
        if filho.visitas == 0:
            return float("inf")

        media = filho.vitorias / filho.visitas
        exploracao = self.c_param * math.sqrt(math.log(max(1, total_visitas_pai)) / filho.visitas)
        return media + exploracao

    def _selecionar_no(self, no):
        while no.movimentos_nao_expandidos == [] and no.filhos:
            no = max(no.filhos, key=lambda f: self._ucb1(f, no.visitas))
        return no

    def _expandir_no(self, no):
        if not no.movimentos_nao_expandidos:
            return no

        movimento = no.movimentos_nao_expandidos.pop()
        novo_tabuleiro = self.realiza_movimento(no.tabuleiro, no.jogador_atual, movimento)
        proximo_jogador = "c" if no.jogador_atual == "o" else "o"
        filho = NoMCTS(novo_tabuleiro, proximo_jogador, movimento, movimento, no)
        filho.movimentos_nao_expandidos = self.gerar_movimentos_legais(
            filho.tabuleiro, filho.jogador_atual, filho.jogada_anterior, self.largura_beam
        )
        no.filhos.append(filho)
        return filho

    def _simular(self, no, historico):
        hash_atual = gerar_hash_tabuleiro(no.tabuleiro)
        if historico.count(hash_atual) > 1:
            return "empate"

        if not no.movimentos_nao_expandidos and not no.filhos:
            return "c" if no.jogador_atual == "o" else "o"

        return self.simular_jogo_aleatorio(
            copia_tabuleiro(no.tabuleiro),
            no.jogador_atual,
            self.max_turnos_sim,
            no.jogada_anterior,
        )

    def _backpropagar(self, no, resultado, jogador_raiz):
        if resultado == "empate":
            valor = 0.5
        elif resultado == jogador_raiz:
            valor = 1.0
        else:
            valor = 0.0

        while no is not None:
            no.visitas += 1
            no.vitorias += valor
            no = no.pai

    def _mcts_escolher_movimento(self, tabuleiro, jogador, historico, jogada_anterior):
        raiz = NoMCTS(copia_tabuleiro(tabuleiro), jogador, jogada_anterior, None, None)
        raiz.movimentos_nao_expandidos = self.gerar_movimentos_legais(
            raiz.tabuleiro,
            raiz.jogador_atual,
            raiz.jogada_anterior,
            self.largura_beam,
        )
        if not raiz.movimentos_nao_expandidos:
            return None

        iteracoes = max(1, self.simulacoes_por_movimento) * max(1, self.largura_beam)

        for _ in range(iteracoes):
            no = raiz
            no = self._selecionar_no(no)
            no_exp = self._expandir_no(no)
            resultado = self._simular(no_exp, historico)
            self._backpropagar(no_exp, resultado, jogador)

        if not raiz.filhos:
            if raiz.movimentos_nao_expandidos:
                return raiz.movimentos_nao_expandidos[0]
            return None

        melhor_filho = max(raiz.filhos, key=lambda f: f.visitas)
        return melhor_filho.movimento

    def escolher_movimento(self, tabuleiro, jogador, historico, jogada_anterior):
        return self._mcts_escolher_movimento(tabuleiro, jogador, historico, jogada_anterior)

    def escolher_movimento_seguro(self, tabuleiro, jogador, historico, jogada_anterior):
        movimento_escolhido = self.escolher_movimento(tabuleiro, jogador, historico, jogada_anterior)

        if movimento_escolhido and validar_movimento(tabuleiro, jogador, movimento_escolhido):
            return movimento_escolhido

        gerador_movimentos = self.gerar_movimentos_onca if jogador == "o" else self.gerar_movimentos_caes
        for movimento in gerador_movimentos(tabuleiro):
            if validar_movimento(tabuleiro, jogador, movimento):
                return movimento

        return None


def escolher_movimento_seguro(tabuleiro, jogador, historico, jogada_anterior, simulacoes_por_movimento=120, largura_beam=6):
    bot = MCTSOnca(simulacoes_por_movimento=simulacoes_por_movimento, largura_beam=largura_beam)
    return bot.escolher_movimento_seguro(tabuleiro, jogador, historico, jogada_anterior)
