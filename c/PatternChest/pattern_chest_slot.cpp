#include "pattern_chest_slot.h"

PatternChestSlot::PatternChestSlot(const unsigned pattern_size){
    this->pattern_size = pattern_size;
    this->patterns = malloc(0);
    this->size = 0;
}
const PatternChestSlot::Pattern* get_pattern(unsigned idx){
    return &this->patterns[idx];
}
const unsigned PatternChestSlot::get_pattern_size(){
    return this->pattern_size;
}
void PatternChestSlot::add_pattern(Pattern pattern){
    this->patterns = realloc(patterns, (this->size + 1) * sizeof(Pattern))
    this->patterns[-1] = pattern;
    this->size = this->size + 1;
}
bool PatternChestSlot::is_exists(Pattern pattern){
    for(unsigned i = 0; i < this->size; i++){
        if(this->patterns[i] == pattern)return true;
    }
    return false;
}

