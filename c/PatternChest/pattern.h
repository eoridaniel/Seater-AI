#include "seat.c"
#include <iostream>

enum type {TopRightCorner, TopLeftCorner, TopSide, LeftSide, Middle, RightSide, BottomRightCorner, BottomLeftSide, BottomSide};
using namespace std;
class Pattern{
    private:
        unsigned row_len;
        unsigned col_len;
        type pattern_type;
        unsigned size;
        const Seat * pattern;
    public:
        Pattern(unsigned row_len, unsigned col_len, type pattern_type, unsigned size, Seat* pattern);
        unsigned get_size();
        type get_pattern_type();
        bool is_free(Seat* seats);
        bool equal(Seat* seats);
        Pattern* rotate();
        void show();
};