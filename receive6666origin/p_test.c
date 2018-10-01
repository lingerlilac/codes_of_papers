#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SIZE 1024

int main()
{
    FILE *fp    = NULL;
    FILE *fp_w  = NULL;
    int read_line = 0;
    int write_line = 0;

    char buffer[SIZE];

    fp = fopen("debug1.txt", "rb");
    if(!fp)
        return -1;
    fp_w = fopen("destructeddata.txt", "wb");
    if(!fp_w)
        return -1;
    memset(buffer, 0, SIZE);
    read_line = fread(buffer, SIZE, 1, fp);
    write_line = fwrite(buffer, SIZE, 1, fp_w);
    while(read_line)
    {
        memset(buffer, 0, SIZE);
        read_line = fread(buffer, SIZE, 1, fp);
        write_line = fwrite(buffer, SIZE, 1, fp_w);        
    }

    if(fp)
        fclose(fp);
    if(fp_w)
        fclose(fp_w);
    return 0;
}