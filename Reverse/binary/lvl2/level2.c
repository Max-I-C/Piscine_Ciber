#include <stdio.h>
#include <string.h>
#include <stdlib.h>


static char	*suite_join(char const *s1, char const *s2, char *new_char, int len1)
{
	int	count;

	count = 0;
	if (s1 && s2)
	{
		while (s1[count] != '\0')
		{
			new_char[count] = s1[count];
			count++;
		}
		count = 0;
		while (s2[count] != '\0')
		{
			new_char[len1] = s2[count];
			count++;
			len1++;
		}
		new_char[len1] = '\0';
		return (new_char);
	}
	return (new_char);
}

char	*ft_strjoin(char const *s1, char const *s2)
{
	int		len1;
	int		len2;
	char	*new_char;

	len1 = strlen(s1);
	len2 = strlen(s2);
	new_char = malloc((len1 + len2 + 1) * sizeof(char));
	if (new_char == NULL)
		return (NULL);
	suite_join(s1, s2, new_char, len1);
	return (new_char);
}


char *ft_crop(char *user_input, int count)
{
    char *crop_char;
    int count_down = 0;

    crop_char = malloc(sizeof(char) * 4);
    if(!crop_char)
        return(NULL);
    while (count_down != 3)
    {
        crop_char[count_down] = user_input[count];
        count_down++;
        count++;
    }
    crop_char[count_down] = '\0';
    return(crop_char);
}

int verif_input()
{
    char user_input[100] = "";
    char user_join[101];
    int count = 2;
    int count_user_final = 1;

    printf("Please enter key: ");
    scanf("%100s", user_input);
    user_join[0] = 'd';
    while (user_input[count])
    {
        char *crop_char = ft_crop(user_input, count);
        count = count + 3;
        int num_ascii = atoi(crop_char);
        free(crop_char);
        user_join[count_user_final] = (char)num_ascii; 
        count_user_final++;
    }
    user_join[count_user_final] = '\0';
    
    if(strcmp(user_join, "delabere"))
        return(1);
    if(user_input[0] != '0' || user_input[1] != '0')
        return(1);
    return(0);
}

int main()
{
    if(verif_input())
        return(printf("Nop\n"), 1);
    return(printf("Good job\n"), 0);
}