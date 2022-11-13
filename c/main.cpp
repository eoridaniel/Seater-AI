#include <cstdlib>
#include <iostream>
#include "PatternChest/pattern.h"

using namespace std;

int main(int argc, char * argv[]){
    Seat* a = (Seat*)malloc(12 * sizeof(Seat));
    for(unsigned i = 0; i < 12; i++){
        a[i].val = (i % 4);
    }

}