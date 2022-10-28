/*#include <cuda.h>*/
#include "pattern.h"

class Pattern{
    private:
        type pattern_type;
        unsigned row_len;
        unsigned col_len;
        const Seat * pattern;
    public:
        Pattern(type pattern_type, unsigned row_len, unsigned col_len, Seat* pattern){
            this->pattern_type = pattern_type;
            this->row_len = row_len;
            this->col_len = col_len;
            this->pattern = pattern;
        }
        unsigned get_row_len(){
            return this->row_len;
        }
        unsigned get_col_len(){
            return this->col_len;
        }
        const Seat* get_pattern(){
            return this->pattern;
        }
        type get_pattern_type(){
            return this->pattern_type;
        }
        bool is_free(Seat* seats){
            
            for(unsigned i = 0; i < row_len * col_len; i++){
                if((pattern[i].val == 1 && seats[i].val != 0) || (pattern[i].val == 0 && seats[i].val == 1)){
                    return false;
                }
            }
            return true;
        }
};
