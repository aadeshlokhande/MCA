
#include<iostream>
using namespace std;
int main()
{
    int arr[100], n, pos, value;
    cout << "enter a number of elements = ";
    cin >> n;

    cout << "enter element:";
    for(int i = 0; i<n; i++)
    {
        cin >> arr[i];
    }

    cout << "givin Array := ";
    for(int i = 0; i<n; i++)
    {
        cout << arr[i]<< ", ";
    }
    cout<<endl;

// =<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=
//      insert
    // cout<<"enter a postion between 0 to "<< n<<" = ";
    // cin >> pos;
    // cout << "enter a value = ";
    // cin >> value;

    // for(int i = n; i>pos; i--)
    // {
    //     arr[i] = arr[i-1];
    // }
    // arr[pos]=value;
    // n++;
    // cout << "inserted Array := ";
    // for(int i = 0; i<n; i++)
    // {
    //     cout << arr[i]<< ", ";
    // }
    // cout<<endl;


//     // =<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=
    // updation
    // cout<<"Enter a postion between 0 to "<< n<<" = ";
    // cin >> pos;
    // cout << "Enter a value = ";
    // cin >> Value;

    // arr[pos] = value;

    // cout << "Updated Array := ";
    // for(int i = 0; i<n; i++)
    // {
    //     cout << arr[i]<< ", ";
    // }
    // cout<<endl;

//     // =<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=

//     // deletion
    // cout<<"enter a postion between 0 to "<< n<<" = ";
    // cin >> pos;

    // for(int i = pos; i<n-1; i++)
    // {
    //     arr[i] = arr[i+1];
    // }
    // n--;
    // cout << "deleted Array := ";
    // for(int i = 0; i<n; i++)
    // {
    //     cout << arr[i]<< ", ";
    // }
    // cout<<endl;


    // =<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=
    // Search

    // int index = -1;
    // cout<<"enter a number to search =";
    // cin >> value;

    // for(int i = 0; i<n; i++)
    // {
    //     if(value==arr[i])
    //     {
    //         index = i;
    //         break;
    //     }
    // }

    // if(index== -1)
    // {
    //     cout<< "value not found";
    // }
    // else 
    // {
    //     cout<<value<< " is found on "<< index<<" index"<<endl;
    // }



    return 0;
}