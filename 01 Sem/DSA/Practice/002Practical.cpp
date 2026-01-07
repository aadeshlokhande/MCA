#include<iostream>
using namespace std;
int main()
{
    int n = 5;
    int arr[n] = {50,20,30,10,40};

    for(int i = 0; i<n; i++)
    {
        cout<< arr[i]<<", ";
    }
    cout<<endl;

    for(int i = 0; i<n-1; i++)
    {
        for(int j = 0; j<n;  j++)
        {
            if(arr[j]>arr[j+1])
            {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }    
    
    
    for(int i = 0; i<n; i++)
    {
        cout<< arr[i]<<", ";
    }
    return 0;
}