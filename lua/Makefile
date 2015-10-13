INC = ./picklingtools/
OCINC = ./picklingtools/opencontainers_1_8_0/include/
LIB = ./picklingtools/Build

WIN_LUA_INC = D:/lua/include
WIN_LUA_LIB = D:/lua/bin

all: libpickle.cpp
ifeq ($(OS), Windows_NT)
	g++ -c -I$(INC) -I$(OCINC) -I$(WIN_LUA_INC) -std=c++11 libpickle.cpp -o libpickle.o
	g++ -shared -L$(LIB) -lptools -L$(WIN_LUA_LIB) -llua libpickle.o -o libpickle.dll
	ar cr libpickle.lib libpickle.o
else
	g++ -fPIC -c -I$(INC) -I/usr/include/lua5.1/ -I$(OCINC) -std=c++11 libpickle.cpp -o libpickle.o
	g++ -shared -L$(LIB)  -llua5.1 -lptools libpickle.o -o libpickle.so
	ar cr libpickle.a libpickle.o
endif
