// Illustrate how an object can be passed as a parameter to a method in Java using a suitable program.


class Student {
    String name;
    int marks;

    Student(String n, int m) {
        name = n;
        marks = m;
    }
}

class Result {
    void display(Student s) {
        System.out.println("Name: " + s.name);
        System.out.println("Marks: " + s.marks);
    }
}

public class ObjectPass {
    public static void main(String[] args) {
        Student s1 = new Student("Amit", 85); 
        Result r = new Result();
        r.display(s1); 
    }
}


