INC = ./picklingtools/
OCINC = ./picklingtools/opencontainers_1_8_0/include/
LIB = ./picklingtools/

all: linux
	
linux: libpickle.cpp
	g++ -fPIC -shared -I$(INC) -I$(OCINC) -L$(LIB) -lptools -std=c++11 libpickle.cpp -o libpickle.so

windows: libpickle.cpp
	g++ -fPIC -shared -I$(INC) -I$(OCINC) -L$(LIB) -lptools -std=c++11 libpickle.cpp -o libpickle.dll
