# machine2019

Commande pour stream camera sur Raspberry Pi:
raspivid -n -fps 30 -vs -w 683 -h 384 -md 4 -o - -t 1000000 | nc -l 2222

Splitter de stream sur les ordi
nc raspberrypi-rose 2222 | tee >(nc -l 2222) | nc -l 2223
