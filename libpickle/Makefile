INC = ./picklingtools/
OCINC = ./picklingtools/opencontainers_1_8_0/include/
LIB = ./picklingtools/

WIN_LUA_INC = D:/lua/include
WIN_LUA_LIB = D:/lua/bin

all: linux
	
linux: libpickle.cpp
	g++ -fPIC -shared -I$(INC) -I$(OCINC) -L$(LIB) -lptools -std=c++11 libpickle.cpp -o libpickle.so

win: libpickle.cpp
	g++ -shared -I$(INC) -I$(OCINC) -I$(WIN_LUA_INC) -L$(LIB) -lptools -L$(WIN_LUA_LIB) -llua -std=c++11 libpickle.cpp -o libpickle.dll
