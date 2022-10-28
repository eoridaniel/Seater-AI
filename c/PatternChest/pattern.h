#include "seat.c"

enum type {TopRightCorner, TopLeftCorner, TopSide, LeftSide, Middle, RightSide, BottomRightCorner, BottomLeftSide, BottomSide};

class Pattern{
    private:
        type patter_type;
        unsigned row_len;
        unsigned col_len;
        const Seat * pattern;
    public:
        Pattern(unsigned row_len, unsigned col_len, Seat* pattern);
        unsigned get_row_len();
        unsigned get_col_len();
        const Seat* get_pattern();
        type get_pattren_type();
        bool is_free(Seat* seats);
};
