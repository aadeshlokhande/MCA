// 1. Apply constructor overloading using a suitable Java program
// import java.util.Scanner;

class Student{
    Student()
    {
        System.out.println("Name = User");
        System.out.println("Age = None");
        System.out.println("Branch : None");
    }

    Student(String name)
    {
        System.out.println("Name = "+name);
        System.out.println("Age = None");
        System.out.println("Branch : None");
    }

    Student(String name, int age)
    {
        System.out.println("name = "+name);
        System.out.println("Age = "+age);
        System.out.println("branch = None");
    }

    Student(String name, int age, String branch)
    {
        System.out.println("name = "+name);
        System.out.println("Age = "+age);
        System.out.println("branch = "+branch);
    }
}




public class constructorOverloading
{
    public static void main(String[] args)
    {
        Student pranaya = new Student("Pranaya",22,"MCA"); 
    }
}

// ****************  *****************