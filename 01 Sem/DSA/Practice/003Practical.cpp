// AIM : Implement a singly linked list with basic operations: insertion, deletion, and traversal
#include <iostream>
using namespace std;

// Node structure
struct Node
{
    int data;
    Node* next;
};

// Insert at end
Node* insert(Node* head, int value)
{
    Node* newNode = new Node();
    newNode->data = value;
    newNode->next = NULL;

    if (head == NULL)
        return newNode;

    Node* temp = head;
    while (temp->next != NULL)
    {
        temp = temp->next;
    }

    temp->next = newNode;
    return head;
}

// Delete by value
Node* deleteNode(Node* head, int value)
{
    if (head == NULL)
        return head;

    if (head->data == value)
    {
        Node* temp = head;
        head = head->next;
        delete temp;
        return head;
    }

    Node* curr = head;
    while (curr->next != NULL && curr->next->data != value)
        curr = curr->next;

    if (curr->next != NULL)
    {
        Node* temp = curr->next;
        curr->next = temp->next;
        delete temp;
    }

    return head;
}

// Traverse list
void traverse(Node* head)
{
    Node* temp = head;
    cout << "Linked List: ";
    while (temp != NULL)
    {
        cout << temp->data << " -> ";
        temp = temp->next;
    }
    cout << "NULL" << endl;
}

int main()
{
    Node* head = NULL;

    cout<< "insertion"<< endl;
    head = insert(head, 10);
    head = insert(head, 20);
    head = insert(head, 30);
    head = insert(head, 50);
    head = insert(head, 80);
    traverse(head);
    cout<< "deletion"<< endl;

    head = deleteNode(head, 20);
    traverse(head);

    return 0;
}
