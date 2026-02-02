// Aim:Implement a stack using arrays in C++, and perform push, pop, and display operations

#include <iostream>
using namespace std;

class Stack 
{
    int *arr;
    int top;
    int size;

    public:
        Stack(int s) 
        {
            size = s;
            arr = new int[size];
            top = -1;
        }

        // Push operation
        void push(int value) 
        {
            if (top == size - 1) 
            {
                cout << "Stack Overflow\n";
                return;
            }
            arr[++top] = value;
        }

        // Pop operation
        void pop() {
            if (top == -1) 
            {
                cout << "Stack Underflow\n";
                return;
            }
            cout << "Popped element: " << arr[top--] << endl;
        }

        // Display operation
        void display() 
        {
            if (top == -1) 
            {
                cout << "Stack is empty\n";
                return;
            }
            cout << "Stack elements: ";
            for (int i = top; i >= 0; i--) 
            {
                cout << arr[i] << " ";
            }
            cout << endl;
        }

};

int main() {    
    Stack s(5);

    s.push(10);
    s.push(20);
    s.push(30);

    s.display();

    s.pop();
    s.display();

    return 0;
}