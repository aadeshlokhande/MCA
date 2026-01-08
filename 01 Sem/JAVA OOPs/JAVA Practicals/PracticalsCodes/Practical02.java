class Student
{
    int age;
    String name;

    void setData(int abc, String xyz)
    {
        age = abc;
        name = xyz;
    }

    void showData()
    {
        System.out.println("age = "+age);
        System.out.println("name = "+name);
    }

};


public class Practical02 {
    public static void main(String[] args)
    {
        Student prem = new Student();
        prem.setData(21, "Premraj");
        prem.showData();
    }
}
