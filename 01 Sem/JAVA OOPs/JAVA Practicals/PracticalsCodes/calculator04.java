// Practical 4: constructor overloading

public class calculator04 {
    public calculator04()
    {
        System.out.println("**** welcome to Calculator ****");
    }

    public calculator04(int a)
    {
        System.out.printf("%d x %d = %d\n", a,a,a*a);
    }

    public calculator04(int a, int b)
    {
        System.out.printf("%d + %d = %d\n",a,b,a+b);
    }

    public static void main(String[] args)
    {
        calculator04 calc1 = new calculator04();
        calculator04 calc2 = new calculator04(10);
        calculator04 calc4 = new calculator04(10,20);
    }

}
