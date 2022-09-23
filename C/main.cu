#include <stdio.h>
#include <cuda.h>

#define N 10000000
#define BLOCK_SIZE 256

__global__ void vector_add(float *a, float *b ,float *out, int n){
    int index = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x* gridDim.x;
    for (int i = index; i < n; i += stride){
        out[i] = a[i]+ b[i];
    }
}

int main(int argc, char * argv[]){
    
    float *h_a, *h_b, *h_out;

    float *d_a, *d_b, *d_out;

    h_a = (float*)malloc(sizeof(float)* N);
    h_b = (float*)malloc(sizeof(float)* N);
    h_out = (float*)malloc(sizeof(float)* N);

    for(int i = 0;i<N;i++)
    {
        h_a[i] = 0.1f;
        h_b[i] = 0.2f;
        h_out[i] = 0;
    }

    cudaMalloc((void**)&d_a,sizeof(float)*N);
    cudaMemcpy(d_a,h_a,sizeof(float)*N,cudaMemcpyHostToDevice);
    cudaMalloc((void**)&d_b,sizeof(float)*N);
    cudaMemcpy(d_b,h_b,sizeof(float)*N,cudaMemcpyHostToDevice);
    cudaMalloc((void**)&d_out,sizeof(float)*N);
    cudaMemcpy(d_out,h_out,sizeof(float)*N,cudaMemcpyHostToDevice);

    int BLOCKS_NUM = (N+BLOCK_SIZE-1)/BLOCK_SIZE;
    vector_add<<<BLOCKS_NUM,BLOCK_SIZE>>>(d_a,d_b, d_out,N);

    cudaDeviceSynchronize();
    cudaMemcpy(h_out,d_out,sizeof(float)*N, cudaMemcpyDeviceToHost);

    for(int i = 0; i<N; i++)
    {
        printf("%f\n",h_out[i]);
    }

    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_out);
    free(h_a);
    free(h_b);
    free(h_out);



    return 0;
}
