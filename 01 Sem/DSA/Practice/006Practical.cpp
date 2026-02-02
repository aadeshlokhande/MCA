// AIM : Implement standard queue operations and a circular queue using arrays

// =<:>=<:>=<:>=<:>= Standard Queue using Array =<:>=<:>=<:>=<:>=<:>=

// #include <iostream>
// using namespace std;

// #define SIZE 5

// int queue[SIZE];
// int front = -1, rear = -1;

// void enqueue(int value)
// {
//     if (rear == SIZE - 1)
//         cout << "Queue Overflow\n";
//     else
//     {
//         if (front == -1)
//             front = 0;
//         rear++;
//         queue[rear] = value;
//     }
// }

// void dequeue()
// {
//     if (front == -1 || front > rear)
//         cout << "Queue Underflow\n";
//     else
//         front++;
// }

// void display()
// {
//     if (front == -1 || front > rear)
//         cout << "Queue is empty\n";
//     else
//     {
//         for (int i = front; i <= rear; i++)
//             cout << queue[i] << " ";
//         cout << endl;
//     }
// }

// int main()
// {
//     enqueue(10);
//     enqueue(20);
//     enqueue(30);
//     display();

//     dequeue();
//     dequeue();
//     dequeue();
//     display();

//     return 0;
// }


// =<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>==<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=
// =<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>==<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=<:>=

// =<:>=<:>=<:>=<:>= Circular Queue using Array =<:>=<:>=<:>=<:>=<:>=

#include <iostream>
using namespace std;

#define SIZE 5

int cqueue[SIZE];
int front = -1, rear = -1;

void enqueue(int value)
{
    if ((rear + 1) % SIZE == front)
        cout << "Circular Queue Overflow\n";
    else
    {
        if (front == -1)
            front = 0;
        rear = (rear + 1) % SIZE;
        cqueue[rear] = value;
    }
}

void dequeue()
{
    if (front == -1)
        cout << "Circular Queue Underflow\n";
    else if (front == rear)
        front = rear = -1;
    else
        front = (front + 1) % SIZE;
}

void display()
{
    if (front == -1)
        cout << "Queue is empty\n";
    else
    {
        int i = front;
        while (true)
        {
            cout << cqueue[i] << " ";
            if (i == rear)
                break;
            i = (i + 1) % SIZE;
        }
        cout << endl;
    }
}

int main()
{
    enqueue(10);
    enqueue(20);
    enqueue(30);
    display();

    dequeue();
    display();

    enqueue(40);
    enqueue(50);
    display();

    return 0;
}
