import sys
import redis

MAXINT = 16
def OUTRO(l): return 'c' if l == 'o' else 'o'
def POS(l, c): return l * 8 + c

def ABS(x): return -x if x < 0 else x

def inicia(argv):
    if len(argv) < 4:
        prog = argv[0]
        print("formato:")
        print(f"  {prog} lado jogadas tempo [ip porta]\n")
        print("   lado: indica que lado inicia o jogo, os valores possíveis são o ou c")
        print("   jogadas: número máximo de jogadas na partida")
        print("   tempo: limite em segundos para cada jogada, 0 indica sem limite")
        print("   ip: opcional (default 127.0.0.1)")
        print("   porta: opcional (default 10001)")
        sys.exit(1)
    lado = argv[1][0]
    jogadas = int(argv[2])
    timeout = int(argv[3])
    ip = argv[4] if len(argv) > 4 else "127.0.0.1"
    porta = int(argv[5]) if len(argv) > 5 else 10001
    r = redis.Redis(host=ip, port=porta, decode_responses=True)
    try:
        r.ping()
    except Exception as e:
        print(f"Erro ao conectar com o servidor redis: {e}")
        sys.exit(1)
    return r, lado, jogadas, timeout

def parse(jogada):
    parts = jogada.strip().split()
    if len(parts) < 2:
        return (False, None, None, None, None, None, None)
    lado = parts[0]
    tipo = parts[1]
    if lado not in ('o', 'c'):
        return (False, None, None, None, None, None, None)
    if tipo == 'n':
        return (True, lado, tipo, 0, [], [], f"{lado} n")
    if tipo not in ('m', 's'):
        return (False, None, None, None, None, None, None)
    p = 2
    mov_l, mov_c = [], []
    if tipo == 'm':
        if len(parts) < p + 4:
            return (False, None, None, None, None, None, None)
        l1, c1, l2, c2 = map(int, parts[p:p+4])
        mov_l = [l1, l2]
        mov_c = [c1, c2]
        num_mov = 1
    else:  # 's'
        if lado != 'o':
            return (False, None, None, None, None, None, None)
        if len(parts) < p + 1:
            return (False, None, None, None, None, None, None)
        num_mov = int(parts[p]); p += 1
        if len(parts) < p + 2 * (num_mov + 1):
            return (False, None, None, None, None, None, None)
        for i in range(num_mov + 1):
            l = int(parts[p]); c = int(parts[p+1]); p += 2
            mov_l.append(l); mov_c.append(c)
    canon = [lado, tipo]
    if tipo == 's':
        canon.append(str(num_mov - 1))
    for i in range(num_mov):
        canon.append(str(mov_l[i])); canon.append(str(mov_c[i]))
    return (True, lado, tipo, num_mov, mov_l, mov_c, " ".join(canon))

def pos_valida(l, c):
    if l < 1 or l > 7 or c < 1 or c > 5:
        return False
    if l == 6 and (c == 1 or c == 5):
        return False
    if l == 7 and (c == 2 or c == 4):
        return False
    return True

def mov_possivel(tipo, lo, co, ld, cd):
    if not pos_valida(lo, co): return False
    if not pos_valida(ld, cd): return False
    distl = ABS(lo - ld)
    distc = ABS(co - cd)
    if (distl + distc) == 0: return False
    if tipo == 'm':
        if lo == 7 and distl == 0:
            return distc == 2
        if (distl > 1) or (distc > 1): return False
        if ((lo + co) % 2) and ((distl + distc) > 1): return False
        if (lo == 5) and (ld == 6) and (co != 3): return False
        if (lo == 6) and ((co % 2) == 0):
            if (ld == 5) and (cd != 3): return False
            if (ld == 7) and (cd == 3): return False
        return True
    if tipo == 's':
        if lo == 7 and distl == 0:
            return distc == 4
        if (distl == 1) or (distc == 1) or (distl + distc) > 4: return False
        if ((lo + co) % 2) and ((distl + distc) > 2): return False
        if (lo == 5) and (ld == 7) and (co != 3): return False
        if (lo == 6) and (ld == 4) and (((co == 2) and (cd != 4)) or ((co == 4) and (cd != 2))):
            return False
        if (lo == 7) and (cd != 3): return False
        return True
    return False

def aplica(tabuleiro, lado, tipo, num_mov, mov_l, mov_c):
    buf = list(tabuleiro)
    if tipo == 'n':
        return True, tabuleiro
    if tipo == 'm':
        l, c = mov_l[0], mov_c[0]
        ln, cn = mov_l[1], mov_c[1]
        if not mov_possivel('m', l, c, ln, cn):
            return False, tabuleiro
        p = POS(l, c)
        if buf[p] != lado: return False, tabuleiro
        pn = POS(ln, cn)
        if buf[pn] != '-': return False, tabuleiro
        buf[p] = '-'
        buf[pn] = lado
    else:
        l, c = mov_l[0], mov_c[0]
        p = POS(l, c)
        if (lado != 'o') or (buf[p] != 'o'):
            return False, tabuleiro
        for i in range(1, num_mov + 1):
            ln, cn = mov_l[i], mov_c[i]
            if not mov_possivel('s', l, c, ln, cn):
                return False, tabuleiro
            buf[p] = '-'
            pn = POS(ln, cn)
            if buf[pn] != '-':
                return False, tabuleiro
            l_mid = (l + ln) // 2
            c_mid = (c + cn) // 2
            pmid = POS(l_mid, c_mid)
            if buf[pmid] != 'c':
                return False, tabuleiro
            buf[pmid] = '-'
            buf[pn] = 'o'
            l, c, p = ln, cn, pn
    return True, "".join(buf)

def vitoria(lado, tab):
    if lado == 'o':
        nc = 0
        for l in range(1, 8):
            for c in range(1, 6):
                if tab[POS(l, c)] == 'c':
                    nc += 1
        return nc <= 9
    for l in range(1, 8):
        for c in range(1, 6):
            if tab[POS(l, c)] == 'o':
                for i in (-1, 0, 1):
                    for j in (-1, 0, 1):
                        if mov_possivel('m', l, c, l + i, c + j) and tab[POS(l + i, c + j)] == '-':
                            return False
                        if mov_possivel('s', l, c, l + 2*i, c + 2*j) and                                tab[POS(l + i, c + j)] == 'c' and                                tab[POS(l + 2*i, c + 2*j)] == '-':
                            return False
                return True
    return False

TABULEIRO_INICIAL = (
    "#######\n"
    "#ccccc#\n"
    "#ccccc#\n"
    "#ccocc#\n"
    "#-----#\n"
    "#-----#\n"
    "# --- #\n"
    "#- - -#\n"
    "#######\n"
)

def main():
    r, quem_joga, num_jogadas, timeout = inicia(sys.argv)
    tabuleiro = TABULEIRO_INICIAL
    vencedor = ' '

    print(f"{num_jogadas}:")
    print(tabuleiro, end="")

    buffer = f"{quem_joga}\n{OUTRO(quem_joga)} n\n{tabuleiro}"
    while num_jogadas:
        key_tab = f"tabuleiro_{quem_joga}"
        r.ltrim(key_tab, 1, 0)
        r.rpush(key_tab, buffer)

        ok = False
        key_jogada = f"jogada_{quem_joga}"
        item = r.blpop(key_jogada, timeout=timeout if timeout > 0 else 0)
        if item is not None:
            jogada = item[1]
            ok_parse, lado, tipo, num_mov, mov_l, mov_c, jogada_canon = parse(jogada)
            if ok_parse and quem_joga == lado:
                ok_aplica, novo_tab = aplica(tabuleiro, lado, tipo, num_mov, mov_l, mov_c)
                if ok_aplica:
                    tabuleiro = novo_tab
                    ok = True
                    jogada_print = jogada_canon
                else:
                    jogada_print = f"{quem_joga} n"
            else:
                jogada_print = f"{quem_joga} n"
        else:
            jogada_print = f"{quem_joga} n"

        print(f"{num_jogadas}: {jogada_print}")
        print(tabuleiro, end="")

        if vitoria(quem_joga, tabuleiro):
            print(f"{num_jogadas}: vitória de {quem_joga}")
            vencedor = quem_joga
            break

        quem_joga = OUTRO(quem_joga)
        buffer = f"{quem_joga}\n{jogada_print}\n{tabuleiro}"
        num_jogadas -= 1
    r.rpush("tabuleiro_o", f"o\nc n\n{tabuleiro}")
    r.rpush("tabuleiro_c", f"c\no n\n{tabuleiro}")

    if num_jogadas == 0:
        print("empate")
    else:
        print(f"vencedor: {vencedor}")

if __name__ == "__main__":
    main()
