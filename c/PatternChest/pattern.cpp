#include "pattern.h"

Pattern::Pattern(unsigned row_len, unsigned col_len, type pattern_type, unsigned size, Seat* pattern){
    this->row_len = row_len;
    this->col_len = col_len;
    this->pattern_type = pattern_type;
    this->size = size;
    this->pattern = pattern;
}
unsigned Pattern::get_size(){
    return this->size;
}
type Pattern::get_pattern_type(){
    return this->pattern_type;
}
bool Pattern::is_free(Seat* seats){
    for(unsigned i = 0; i < this->size; i++){
        if((this->pattern[i].val == 1 && seats[i].val != 0) || (this->pattern[i].val == 0 && seats[i].val == 1)){
            return false;
        }
    }
    return true;
}
bool Pattern::equal(Seat* seats){
    for(unsigned i = 0; i <  this->size; i++){
        if(this->pattern[i].val != seats[i].val)return false;
    }
    return true;
}
Pattern* Pattern::rotate(){
    Seat* rotated = (Seat*)malloc(size * sizeof(Seat));
    for(unsigned i = 0; i < this->col_len; i++)
        for(unsigned j = 0;j < this->row_len; j++)
            rotated [j * this->col_len + i].val = this->pattern[ i * this->row_len + j].val;
    unsigned tmp = 0;
        for(unsigned j = 0;j < this->row_len; j++)
         for(unsigned i = 0; i < (this->col_len / 2); i++){
            tmp = rotated[((j+1) * this->col_len - 1) - i].val;
            rotated [((j + 1) * this->col_len - 1) - i].val = rotated[j * this->col_len + i].val;
            rotated[ j * this->col_len + i].val = tmp;
        }
    return new Pattern(this->col_len, this->row_len, this->pattern_type, this->size, rotated);
}
void Pattern::show(){
    for(unsigned i = 0; i < this->size; i++){
        cout << this->pattern[i].val << (((i + 1) % this->row_len == 0) ? "\n" : ",");
    }
}
