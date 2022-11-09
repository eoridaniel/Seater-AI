#include <cstdlib>
#include <iostream>
#include "PatternChest/pattern.h"

using namespace std;

int main(int argc, char * argv[]){
    Seat* a = (Seat*)malloc(12 * sizeof(Seat));
    for(unsigned i = 0; i < 12; i++){
        a[i].val = (i % 4);
    }
    Pattern* p = new Pattern(3,4,Middle,12,a);
    p->show();
    Pattern* b = p->rotate();
    cout << endl;
    b->show();

}