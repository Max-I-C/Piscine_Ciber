#include <stdio.h>
#include <string.h>

int verif_input()
{
    char user_input[50];
    printf("Please enter key: ");
    scanf("%50s", user_input);
    if(strcmp(user_input, "__stack_check") == 0)
        return(0);
    return(1);
}

int main(void)
{
    if(verif_input())
        return(printf("Nope.\n"), 1);
    return(printf("Good job.\n"), 0);
}