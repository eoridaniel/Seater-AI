#include "pattern.h"

class PatternChestSlot{
    private:
        const unsigned pattern_size;
        const Pattern* patterns;
    public:
        PatternChestSlot(const unsigned pattern_size, const Pattern* patterns);
        const Pattern* get_pattern(unsigned idx);
        const unsigned get_pattern_size();
};