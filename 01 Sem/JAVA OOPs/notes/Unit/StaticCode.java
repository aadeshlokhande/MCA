class Student {

    String name;          // instance variable
    static int count = 0; // static data member

    // Constructor
    Student(String name) {
        this.name = name;
        count++;   // increases every time object is created
    }

    void display() {
        System.out.println("Name: " + name);
    }

    static void showCount() {
        System.out.println("Total Students: " + count);
    }
}

public class StaticCode {
    public static void main(String[] args) {

        Student s1 = new Student("Amit");
        Student s2 = new Student("Rahul");
        Student s3 = new Student("Sneha");

        s1.display();
        s2.display();
        s3.display();

        Student.showCount();  // calling static method using class name
    }
}
