#include "pattern_chest_slot.h"

PatternChestSlot::PatternChestSlot(unsigned pattern_size){
    this->pattern_size = pattern_size;
    this->patterns = (Pattern*)malloc(0);
    this->size = 0;
}
Pattern* PatternChestSlot::get_pattern(unsigned idx){
    return &this->patterns[idx];
}
unsigned PatternChestSlot::get_pattern_size(){
    return this->pattern_size;
}
void PatternChestSlot::add_pattern(Pattern* pattern){
    this->patterns = (Pattern*)realloc(patterns, (++this->size) * sizeof(Pattern));
    this->patterns[-1] = *pattern;
    this->size = this->size + 1;
}
bool PatternChestSlot::is_exists(Pattern pattern){
    for(unsigned i = 0; i < this->size; i++){
        if(this->patterns[i] == pattern)return true;
    }
    return false;
}
void PatternChestSlot::show(){
    for(unsigned i = 0; i < this->size; i++){
        this->patterns[i].show();
        cout << " ";
    }
    cout << endl;
}

