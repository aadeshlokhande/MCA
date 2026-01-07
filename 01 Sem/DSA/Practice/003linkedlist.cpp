#include <iostream>
using namespace std;

// Node class
class Node 
{
public:
    int data;
    Node* next;

    Node(int value) {
        data = value;
        next = NULL;
    }
};

// Insert at beginning
void insertAtBegin(Node*& head, int value) 
{
    Node* newNode = new Node(value);
    newNode->next = head;
    head = newNode;
}

// Insert at end
void insertAtEnd(Node*& head, int value) 
{
    Node* newNode = new Node(value);

    if (head == NULL) {
        head = newNode;
        return;
    }

    Node* temp = head;
    while (temp->next != NULL) 
    {
        temp = temp->next;
    }
    temp->next = newNode;
}

// Delete from beginning
void deleteAtBegin(Node*& head) 
{
    if (head == NULL) return;

    Node* temp = head;
    head = head->next;
    delete temp;
}

// Delete from end
void deleteAtEnd(Node*& head) 
{
    if (head == NULL) return;

    if (head->next == NULL) {
        delete head;
        head = NULL;
        return;
    }

    Node* temp = head;
    while (temp->next->next != NULL) {
        temp = temp->next;
    }

    delete temp->next;
    temp->next = NULL;
}

// Traversal
void traverse(Node* head) {
    Node* temp = head;
    while (temp != NULL) {
        cout << temp->data << " -> ";
        temp = temp->next;
    }
    cout << "NULL";
}

// Main function
int main() {
    Node* head = NULL;

    insertAtBegin(head, 10);
    insertAtBegin(head, 20);
    insertAtEnd(head, 30);
    insertAtEnd(head, 40);

    cout << "Linked List: ";
    traverse(head);

    deleteAtBegin(head);
    cout << "\nAfter delete at begin: ";
    traverse(head);

    deleteAtEnd(head);
    cout << "\nAfter delete at end: ";
    traverse(head);

    return 0;
}
