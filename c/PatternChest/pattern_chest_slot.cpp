#include "pattern_chest_slot.h"

class PatternChestSlot{
    private:
        unsigned pattern_size;
        const Pattern* patterns;
    public:
        PatternChestSlot(const unsigned pattern_size, const Pattern* patterns){
            this->pattern_size = pattern_size;
            this->patterns = patterns;
        }
        const Pattern* get_pattern(unsigned idx){
            return &this->patterns[idx];
        }
        const unsigned get_pattern_size(){
            return this->pattern_size;
        }
};