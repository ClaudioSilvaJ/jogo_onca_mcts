Participantes:
Claudio Honorio da Silva Junior
Mateus Heck Soares
Pedro Pivetta Barrotti

O programa tabuleiro.py e controlador.py foram feitos com base nos controladores originais na linguagem C.

Para executar o algoritmo:

Instalar as dependencias (redis):
pip3 install -r requirements.txt

Um console deve rodar:
redis-server redis.conf

Outro console deve rodar o controlador:
python3 controlador.py o 50 0

Outro console(onca):
python3 start_bot_mct.py o

Outro console(cachorro):
python3 start_bot_mct.py c

Obs: O algoritmo também funciona caso o controlador em C esteja sendo rodado nesse caso basta somente que o controlador e o servidor redis estejam rodando e executar:
python3 start_bot_mct.py o
