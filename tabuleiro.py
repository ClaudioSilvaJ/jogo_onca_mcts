import sys
from typing import Optional
import redis

_r: Optional[redis.Redis] = None
_lado: Optional[str] = None

def tabuleiro_conecta(argc: int, argv):
    global _r, _lado
    if argc < 2:
        prog = argv[0] if argv else "programa"
        print("formato:")
        print(f"         {prog} lado [ip porta]\n")
        print("   lado: indica com que peças jogar, os valores possíveis são o ou c")
        print("   ip: parâmetro opcional que indica o ip/hostname do servidor redis")
        print("       o valor default é 127.0.0.1")
        print("   porta: parâmetro opcional que indica a porta do servidor redis")
        print("          o valor default é 10001")
        sys.exit(1)

    _lado = argv[1][0]
    ip = argv[2] if argc > 2 else "127.0.0.1"
    porta = int(argv[3]) if argc > 3 else 10001

    try:
        _r = redis.Redis(host=ip, port=porta, decode_responses=True)
        _r.ping()
    except Exception as e:
        print(f"Não foi possível conectar com o servidor redis: {e}")
        sys.exit(1)

def tabuleiro_envia(buffer: str):
    global _r, _lado
    assert _r is not None and _lado is not None, "chame tabuleiro_conecta primeiro"
    key = f"jogada_{_lado}"
    _r.rpush(key, buffer)

def tabuleiro_recebe() -> str:
    global _r, _lado
    assert _r is not None and _lado is not None, "chame tabuleiro_conecta primeiro"
    key = f"tabuleiro_{_lado}"
    item = _r.blpop(key, timeout=0)
    return item[1] if item else ""
