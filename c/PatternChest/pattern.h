#include "seat.c"
#include <iostream>

enum pattern_type {TopRightCorner, TopLeftCorner, TopSide, LeftSide, Middle, RightSide, BottomRightCorner, BottomLeftSide, BottomSide};
using namespace std;
class Pattern{
    private:
        unsigned row_len;
        unsigned col_len;
        pattern_type type;
        unsigned size;
        const Seat * pattern;
    public:
        Pattern(unsigned row_len, unsigned col_len, pattern_type type, unsigned size, Seat* pattern);
        unsigned get_size();
        pattern_type get_type();
        bool is_free(Seat* seats);
        bool equal(Seat* seats);
        Pattern* rotate();
        void show();
        bool operator== (const Pattern& obj);
};