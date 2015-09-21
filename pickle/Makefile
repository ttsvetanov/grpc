INC = ./picklingtools/
OCINC = ./picklingtools/opencontainers_1_8_0/include/
LIB = ./picklingtools/

all: libpickle.cpp
	g++ -fPIC -shared -I$(INC) -I$(OCINC) -L$(LIB) -lptools -std=c++11 libpickle.cpp -o libpickle.so
