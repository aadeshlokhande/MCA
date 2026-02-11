//  Demonstrate method overloading using a suitable Java program

class calculator{
    
    void calc()
    {
        System.out.println("this is calc");
    }

    void calc(int a, int b)
    {
        System.out.println(a+b);
    }

    void calc(int a, double b)
    {
        System.out.println(a-b);
    }

    void calc(double a, double b)
    {
        System.out.println(a/b);
    }

    void calc(double a, int b)
    {
        System.out.println(a*b);
    }


}



public class methodOverloading {
    public static void main(String[] args)
    {
        calculator c = new calculator();
        c.calc(10.0,20.0);
    }
}
