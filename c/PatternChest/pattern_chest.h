#include "pattern_chest_slot.h"

class PatternChest{
    private:
        unsigned size; //count of slots
        const PatternChestSlot* slots;

        void insert_into_slot(const unsigned size, Pattern pattern);
    public:
        PatternChest(const unsigned size);
        void generate_patterns();

};