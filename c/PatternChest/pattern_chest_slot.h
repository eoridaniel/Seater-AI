#include "pattern.h"

class PatternChestSlot{
    private:
        unsigned pattern_size;
        Pattern* patterns;
        unsigned size;
    public:
        PatternChestSlot(unsigned pattern_size);
        Pattern* get_pattern(unsigned idx);
        unsigned get_pattern_size();
        void add_pattern(Pattern* pattern);
        bool is_exists(Pattern pattern);
        void show();
};