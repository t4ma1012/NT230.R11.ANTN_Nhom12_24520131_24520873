all: task11_demo payload.bin

payload.o: payload.asm
	nasm -f elf64 payload.asm -o payload.o

payload.bin: payload.asm
	nasm -f bin payload.asm -o payload.bin

task11_demo: demo.o payload.o
	gcc -no-pie demo.o payload.o -o task11_demo

demo.o: demo.c
	gcc -g -c -Wall -Wextra -O0 demo.c -o demo.o

run: all
	./task11_demo

inspect: payload.bin
	xxd -g 1 payload.bin
	ndisasm -b 64 payload.bin

clean:
	rm -f demo.o payload.o payload.bin task11_demo
