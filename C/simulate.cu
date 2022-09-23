#include <cuda.h>
#include <iostream>
#include <stdlib.h>
#include <cstdlib>
#include <time.h>
#include <math.h>
#include <utility>

#define THREAD_COUNT 1024

struct Seat{
    unsigned int val : 2;
    // 0 not reserved, 1 reserved, 3 not seat 
};

class FreeSeats{
    public:
        float row;
        float first_seat;
        float free_count;

        __device__ FreeSeats(float row, float first_seat, float free_count){
            this->row = row;
            this->first_seat = first_seat;
            this->free_count = free_count;
        }
        __device__ ~FreeSeats(){
            free(&row);
            free(&first_seat);
            free(&free_count);
        }
};

class Seats{
    private:
        unsigned int max_group_size;
        unsigned int row_len;
        unsigned int col_len;
        unsigned int size;
        unsigned int fsg_size;
        FreeSeats* free_seat_groups;
        Seat* seats;        //row*row_len+col = idx
        bool* shifting;
        int* groups;

        __device__ bool is_free(int row, int first_seat, int required_seats){
            int seat_max_pos = first_seat + required_seats; 
            if(row < this->col_len && seat_max_pos <= this->row_len){
                //current row
                for(int i = (first_seat > 0 ? (first_seat - 1): first_seat) ; i < seat_max_pos; i++){
                    if(this->seats[(row*this->row_len)+i].val == (1 || 3)){
                        return false;
                    }
                }
                //previus row
                if(row > 0){
                    for(int i = ((this->shifting[row] == false && this->shifting[row-1] == false) || (this->shifting[row] && this->shifting[row-1]) ?
                    first_seat : (first_seat > 0 ? (first_seat - 1): first_seat));
                    i < (((this->shifting[row] == false && this->shifting[row-1] == false) || (this->shifting[row] && this->shifting[row-1])) ?
                    seat_max_pos  : (seat_max_pos < (row_len - 1) ? (seat_max_pos + 1) : seat_max_pos)); i++){
                        if(this->seats[((row-1)*this->row_len)+i].val == 1){
                            return false;
                        }
                    }
                }
                //next row
                if(row < (this->col_len - 1)){
                    for(int i = ((this->shifting[row] == false && this->shifting[row+1] == false) || (this->shifting[row] && this->shifting[row+1]) ?
                    first_seat : (first_seat > 0 ? (first_seat - 1): first_seat));
                    i < (((this->shifting[row] == false && this->shifting[row+1] == false) || (this->shifting[row] && this->shifting[row+1])) ?
                    seat_max_pos  : (seat_max_pos < (row_len - 1) ? (seat_max_pos + 1) : seat_max_pos)); i++){
                        if(this->seats[((row+1)*this->row_len)+i].val == 1){
                            return false;
                        }
                    }
                }
                return true;
            }
            return false;
        }
        __device__ void search_free_seat_groups(){
            int incrise = (int)((this->row_len + this->col_len) / 4);
            this->fsg_size = incrise;
            int idx = 0;
            free(this->free_seat_groups);
            this->free_seat_groups = (FreeSeats*)malloc(this->fsg_size * sizeof(FreeSeats));
            for(int row = 0; row < this->col_len; row++){
                float first_free = 0;
                float free_count = 0;
                for(int col = 0; col < this->row_len; col++){
                    if(this->is_free(row, col, 1)){
                        free_count += 1;
                        continue;
                    }else if(free_count > 0){
                        //Realloc
                        if(idx >= this->fsg_size){
                            FreeSeats* tmp = (FreeSeats*)malloc((this->fsg_size + incrise) * sizeof(FreeSeats));
                            for(int i = 0; i < this->fsg_size; i++){tmp[i] = this->free_seat_groups[i];}
                            this->fsg_size += incrise;
                            free(this->free_seat_groups);
                            this->free_seat_groups = tmp;
                        }
                        //
                        this->free_seat_groups[idx++] =  FreeSeats(row, first_free, free_count);
                    }
                    first_free = col + 1;
                    free_count = 0;
                }
                if(first_free < this->row_len){
                    //Realloc
                    if(idx >= this->fsg_size){
                        FreeSeats* tmp = (FreeSeats*)malloc((this->fsg_size + incrise) * sizeof(FreeSeats));
                        for(int i = 0; i < this->fsg_size; i++){tmp[i] = this->free_seat_groups[i];}
                        this->fsg_size += incrise;
                        free(this->free_seat_groups);
                        this->free_seat_groups = tmp;
                    }
                    //
                    this->free_seat_groups[idx++] = FreeSeats(row, first_free, free_count);
                }
            }
            //Resize the final array
            int tp = 0;
            for(int i = 0; i < this->fsg_size; i++){
                if(free_seat_groups[i].free_count < 1){tp++;}
            }
            FreeSeats* tmp = (FreeSeats*)malloc((this->fsg_size - tp) * sizeof(FreeSeats));
            for(int i = 0; i < this->fsg_size - tp; i++){tmp[i] = this->free_seat_groups[i];}
            this->fsg_size -= tp;
            free(this->free_seat_groups);
            this->free_seat_groups = tmp;
        }
        __device__ FreeSeats search_best_seats(int required_seats){
            FreeSeats best_seats = FreeSeats(INFINITY, INFINITY, INFINITY);
            if(this->fsg_size > 0){
                for(int i = 0; i < this->fsg_size; i++){
                    if(0 <= (this->free_seat_groups[i].free_count - required_seats) && (this->free_seat_groups[i].free_count - required_seats) < (best_seats.free_count - required_seats)){
                        best_seats = this->free_seat_groups[i];
                    }
                }
            }
            return best_seats;
        }
        __device__ FreeSeats search_worst_seats(int required_seats){
            FreeSeats worst_seats = FreeSeats(-INFINITY, -INFINITY, -INFINITY);
            if(this->fsg_size > 0){
                for(int i = 0; i < this->fsg_size; i++){
                    if(0 <= (this->free_seat_groups[i].free_count - required_seats) && (this->free_seat_groups[i].free_count - required_seats) > (worst_seats.free_count - required_seats)){
                        worst_seats = this->free_seat_groups[i];
                    }
                }
            }
            return worst_seats;
        }
        __device__ void best_fit(int required_seats){
            if(required_seats <= this->max_group_size){
                this->search_free_seat_groups();
                FreeSeats best_seats = this->search_best_seats(required_seats);
                if(best_seats.free_count != INFINITY && this->is_free(best_seats.row, best_seats.first_seat, required_seats)){
                    this->reserve(best_seats.row, best_seats.first_seat, required_seats);
                    return;
                }
            }
        }
        __device__ void worst_fit(int required_seats){
            if(required_seats <= this->max_group_size){
                this->search_free_seat_groups();
                FreeSeats worst_seats = this->search_worst_seats(required_seats);
                if(worst_seats.free_count != -INFINITY && this->is_free(worst_seats.row, worst_seats.first_seat, required_seats)){
                    this->reserve(worst_seats.row, worst_seats.first_seat, required_seats);
                    return;
                }
            }
        }
        __device__ void first_fit(int required_seats){
            if(this->max_group_size >=  required_seats){
                for(int i = 0; i <  this->size; i++){
                    if(this->is_free((int)(i/this->row_len),i % this->row_len, required_seats)){
                        this->reserve((int)(i/this->row_len), i % this->row_len, required_seats);
                        return;
                    }
                }
            }
        }
        __device__ void reserve(int row, int first_seat, int required_seats){
            for(int i = (row * this->row_len + first_seat); i < (row * this->row_len + first_seat + required_seats); i++){
                this->seats[i].val = 1;
            }
        }
        __device__ int score(){
            int reserved_count = 0;
            for(int i = 0; i < this->size; i++){
                if(this->seats[i].val == 1){
                    reserved_count++;
                }
            }
            return reserved_count;
        }

    public:
        __device__ Seats(int max_group_size, Seat *seats, bool *shifting, int row_len, int col_len, int* groups){
            this->max_group_size = max_group_size;
            this->row_len = row_len;
            this->col_len = col_len;
            this->groups = groups;
            this->seats = seats;
            this->shifting = shifting;
            this->size = this->row_len * this->col_len;
        }
        ~Seats(){
            free(&this->row_len);
            free(&this->col_len);
            free(&this->max_group_size);
            free(&this->size);
        }
        __device__ int wf_simulate(){
            for(int i = 0; i < (int)(this->size * 0.6); i++){
                this->worst_fit(this->groups[i]);
            }
            return this->score();
        }
        __device__ int bf_simulate(){
            for(int i = 0; i < (int)(this->size * 0.6); i++){
                this->best_fit(this->groups[i]);
            }
            return this->score();
        }
        __device__ int ff_simulate(){
            for(int i = 0; i < (int)(this->size * 0.6); i++){
                this->first_fit(this->groups[i]);
            }
            return this->score();
        }
};

__global__ void train(Seat** seats, bool* shifting, int max_group_size, int row_len, int col_len, int* res, int** groups, int block_idx, int block_count){
    Seats *a = new Seats(max_group_size, seats[(block_idx * THREAD_COUNT) + threadIdx.x], shifting, row_len,col_len, groups[(block_idx * THREAD_COUNT) + threadIdx.x]);
    if((block_idx * THREAD_COUNT) + threadIdx.x > (block_count * THREAD_COUNT / 3 * 2)){
        res[(block_idx * THREAD_COUNT) + threadIdx.x] = a->wf_simulate();
    }else if((block_idx * THREAD_COUNT) + threadIdx.x > (block_count * THREAD_COUNT / 3)){
        res[(block_idx * THREAD_COUNT) + threadIdx.x] = a->bf_simulate();
    }
    else{
        res[(block_idx * THREAD_COUNT) + threadIdx.x] = a->ff_simulate();
    }
    printf("%i,", res[block_idx * THREAD_COUNT + threadIdx.x]);
} 

int main(int argc, char * argv[]){

    //Set simulation parameters
    clock_t start = clock();
    unsigned int sim_count = 10000;
    const unsigned int block_count = ((int)sim_count % THREAD_COUNT == 0) ? (sim_count/THREAD_COUNT) : ((int)(sim_count/THREAD_COUNT+1));
    sim_count = block_count * THREAD_COUNT;

    //Prepare rooms and rooms' parameters
    unsigned int col_len  = 35, row_len = 35, max_group_size = 4, group_count = ((int)(row_len * col_len * 0.6));
    
    srand(time(NULL));
    int** groups = (int**)malloc(sim_count*sizeof(int*));
    for(int i = 0; i < sim_count; i++){
        groups[i] = (int*)malloc(group_count*sizeof(int));
        for(int j = 0; j < group_count; j++){
            groups[i][j] = rand() % max_group_size + 1;
        }
    }
    
    int* res = (int*)malloc(sim_count*sizeof(int));
    for(int i = 0; i < sim_count; i++){
        res[i] = 0;
    }

    Seat**  seats = (Seat**)malloc(sim_count*sizeof(Seat*));
    for (int i = 0; i < sim_count; i++){
        seats[i] = (Seat*) malloc(row_len*col_len*sizeof(Seat));
        for(int j = 0; j < row_len*col_len; j++){
            seats[i][j].val = 0;
        }
    }

    bool* shifting = (bool*)malloc(col_len*sizeof(bool));
    for(int i = 0 ; i < col_len; i++){
        shifting[i] = false;
    }

    //Allocate memory on GPU and copy data into VRAM
    Seat** d_seats;
    Seat* temp[sim_count];
    bool* d_shifting;
    int* d_res;
    int** d_groups;
    int* gtemp[sim_count];
    

    cudaMalloc((void**)&d_seats, sim_count*sizeof(Seat*));
    for(int i = 0; i < sim_count; i++){
        cudaMalloc(&(temp[i]), row_len*col_len*sizeof(Seat));
    }
    cudaMemcpy(d_seats,temp,sizeof(Seat*)*sim_count,cudaMemcpyHostToDevice);
    for(int i = 0; i < sim_count; i++){
        cudaMemcpy(temp[i], seats[i], row_len*col_len*sizeof(Seat), cudaMemcpyHostToDevice);
    }
    cudaMalloc((void**)&d_shifting,sizeof(bool)*col_len);
    cudaMemcpy(d_shifting,shifting,sizeof(bool)*col_len,cudaMemcpyHostToDevice);
    
    cudaMalloc((void**)&d_res,sizeof(int)*sim_count);
    cudaMemcpy(d_res, res, sizeof(int)*sim_count, cudaMemcpyHostToDevice);

    cudaMalloc((void**)&d_groups, sim_count*sizeof(int*));
    for(int i = 0; i < sim_count; i++){
        cudaMalloc(&(gtemp[i]), group_count*sizeof(int));
    }
    cudaMemcpy(d_groups,gtemp,sizeof(int*)*sim_count,cudaMemcpyHostToDevice);
    for(int i = 0; i < sim_count; i++){
        cudaMemcpy(gtemp[i], groups[i], group_count*sizeof(Seat), cudaMemcpyHostToDevice);
    }

    //Simulate
    for(int i = 0; i < block_count; i++){    
        printf("%i\n", i*THREAD_COUNT);    
        train<<<1, THREAD_COUNT>>>(d_seats, d_shifting, max_group_size, row_len, col_len, d_res, d_groups, i, block_count);
        /*for(int j = (i*THREAD_COUNT); j < ((i+1)*THREAD_COUNT); j++){
            cudaMemcpy(seats[j], temp[j], sizeof(Seat)*row_len*col_len, cudaMemcpyDeviceToHost);
        }
        cudaMemcpy(res, d_res, sizeof(int)*sim_count, cudaMemcpyDeviceToHost);*/
    }
    
    for(int i = 0; i < sim_count; i++){
        printf("%i %i,", res[i], seats[i][0].val);
    }

    for(int i = 0; i < sim_count; i++){
        cudaFree(temp[i]);
    }
    cudaFree(d_seats);
    for(int i = 0; i < sim_count; i++){
        cudaFree(gtemp[i]);
    }
    cudaFree(d_groups);
    cudaFree(d_res);
    cudaFree(d_shifting);
    clock_t stop = clock();
    printf("\n%f ", ((double)((stop-start)/CLOCKS_PER_SEC)));

    //Write Rresoult into database

    return 0;
}