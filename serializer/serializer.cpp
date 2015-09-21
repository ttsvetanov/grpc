/*
 * =====================================================================================
 *
 *       Filename:  serializer.cpp
 *
 *    Description:  c++ implementated lua package serializer, using picklingtools
 *
 *        Version:  1.0
 *        Created:  09/18/2015 04:55:45 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Guo Ang (Bruce Guo), mail@guoang.me
 *   Organization:  
 *
 * =====================================================================================
 */
#include <cstdlib>
#include <lua.hpp>
#include <chooseser.h>

using namespace std;

namespace {

    int load(lua_State *L) {
        /* convert data stream to val */
        const char * data_stream = lua_tostring(L, 1);
        Array<char> data_arr;
        for (int i = 0; i < strlen(data_stream); i++) {
            data_arr.append(data_stream[i]);
        }
        Val data_val;
        LoadValFromArray(data_arr, data_val);

        unbox(L, data_val);
    }

    /* the first unbox
     * convert python type to lua type recursive
     * retain label
     * then lua unbox read the label to find local ref
     */
    void unbox(lua_State *L, Val data_val) {

        switch (data_val.tag) {
            // python numbers --> lua number
            case 's':
            case 'S':
            case 'i':
            case 'I':
            case 'x':
            case 'X':
            case 'f':
            case 'd':
            case 'q':
            case 'Q':
                lua_Number n = data_val; //lua_Number is double by default
                lua_pushnumber(L, n);
                break;

            // python complex --> ignored
            case 'F':
            case 'D':
                break;

            // python string --> lua string
            case 'a':
                lua_pushstring(L, string(data_val).c_str());
                break;

            // python tuple --> lua table
            case 'u':
                // create a table in top of stack
                lua_newtable(L);
                int table_index = lua_gettop(L);
                Arr val_arr = data_val;
                // for each val in array, unbox it.
                // the unbox automatic push the result in top
                // of the stack.
                // then insert the (i, val) into the table we just created.
                for (int i = 0; i < val_arr.length(); i++) {
                    lua_pushnumber(L, i+1); // the table index start from 1
                    unbox(L, val_arr[i]);
                    lua_settable(L, table_index);
                }
                break;

            // python list --> lua table
            case 'n':
                // just like the tuple
                lua_newtable(L);
                int table_index = lua_gettop(L);
                Arr val_arr = data_val;
                for (int i = 0; i < val_arr.length(); i++) {
                    lua_pushnumber(L, i+1);
                    unbox(L, val_arr[i]);
                    lua_settable(L, table_index);
                }
                break;

            // python dict --> lua table
            case 't':
                lua_newtable(L);
                int table_index = lua_gettop(L);
                Tab val_tab = data_val;
                for (It ii(val_tab); ii(); ) {
                    unbox(L, ii.key());
                    unbox(L, ii.value());
                    lua_settable(L, table_index);
                }
                break;

            //python ordereddict --> lua table
            case 'o':
                lua_newtable(L);
                int table_index = lua_gettop(L);
                OTab val_otab = data_val;
                for (It ii(val_otab); ii();) {
                    unbox(L, ii.key());
                    unbox(L, ii.value());
                    lua_settable(L, table_index);
                }
                break;

            // python None --> lua nil
            case 'Z':
                lua_pushnil(L);
                break;
        }
    }
}
