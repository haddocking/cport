CC = g++
CFLAGS = -O2

.cpp.o:
	$(CC) $(CFLAGS) -c $<

resdist: resdist.o
	$(CC) $(CFLAGS) -o $@ resdist.o

clean: 
	rm -f resdist resdist.o
