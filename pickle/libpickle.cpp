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
#include <lua.hpp>
#include <chooseser.h>

using namespace std;

namespace {
    int dump(lua_State *L);
    int load(lua_State *L);
    Val box(lua_State *L, int index);
    void unbox(lua_State *L, Val data_val);

    int dump(lua_State *L) {
        /* there is a table in stack, box it */
        Val data_val = box(L, lua_gettop(L));
        Array<char> data_arr;
        DumpValToArray(data_val, data_arr);

        lua_pushstring(L, data_arr.data());
        return 1;
    }

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
        return 1;
    }

    /* the second box
     * convert lua type to python type recursive
     * retain label
     * then dump() serialize it to data stream
     */
    Val box(lua_State *L, int index) {
        Val res;
        if (lua_isnoneornil(L, index)) // invalid index or nil
            return res;
        else if (lua_isboolean(L, index))
            res = lua_toboolean(L, index);
        else if (lua_isnumber(L, index))
            res = lua_tonumber(L, index);
        else if (lua_isstring(L, index))
            res = lua_tostring(L, index);

        // actually, there is no table, all table has
        // been convert to NerRef. the tables here is
        // just Tuple.
        else if (lua_istable(L, index)) {
            lua_pushnil(L);
            Arr a;
            while (lua_next(L, index) != 0) {
                a.append(box(L, lua_gettop(L)));
                lua_pop(L, 1);
            }
            res = a;
        }
        return res;
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
                {
                    lua_Number n = data_val; //lua_Number is double by default
                    lua_pushnumber(L, n);
                    break;
                }

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
                {
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
                }

            // python list --> lua table
            case 'n':
                {
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
                }

            // python dict --> lua table
            case 't':
                {
                    lua_newtable(L);
                    int table_index = lua_gettop(L);
                    Tab val_tab = data_val;
                    for (It ii(val_tab); ii(); ) {
                        unbox(L, ii.key());
                        unbox(L, ii.value());
                        lua_settable(L, table_index);
                    }
                    break;
                }

            //python ordereddict --> lua table
            case 'o':
                {
                    lua_newtable(L);
                    int table_index = lua_gettop(L);
                    OTab val_otab = data_val;
                    for (It ii(val_otab); ii();) {
                        unbox(L, ii.key());
                        unbox(L, ii.value());
                        lua_settable(L, table_index);
                    }
                    break;
                }

            // python None --> lua nil
            case 'Z':
                lua_pushnil(L);
                break;
        }
    }

    const struct luaL_Reg libpickle[] = {
        {"dump", dump},
        {"load", load},
        {NULL, NULL}
    };

}

extern "C" int luaopen_libpickle (lua_State *L) {
    luaL_newlib(L, libpickle);
    return 1;
}
