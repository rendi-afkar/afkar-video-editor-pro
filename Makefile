.PHONY: all install clean

all: install main

install:
	pkg install -y python python-cryptography ffmpeg clang git

main: main.c
	cc -O2 -Wall -Wextra -o main main.c
	@echo "[OK] Selesai. Jalankan dengan: ./main"

clean:
	rm -f main
