INC = ./picklingtools/
OCINC = ./picklingtools/opencontainers_1_8_0/include/
LIB = ./picklingtools/Build

WIN_LUA_INC = D:/lua/include
WIN_LUA_LIB = D:/lua/bin

all: libpickle.cpp
ifeq ($(OS), Windows_NT)
	g++ -shared -I$(INC) -I$(OCINC) -I$(WIN_LUA_INC) -L$(LIB) -lptools -L$(WIN_LUA_LIB) -llua -std=c++11 libpickle.cpp -o libpickle.dll
else
	g++ -fPIC -shared -I$(INC) -I$(OCINC) -L$(LIB) -lptools -std=c++11 libpickle.cpp -o libpickle.so
endif
