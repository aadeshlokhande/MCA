// Practical 4: constructor overloading

public class calculator {
    public calculator()
    {
        System.out.println("**** welcome to Calculator ****");
    }

    public calculator(int a)
    {
        System.out.printf("%d x %d = %d\n", a,a,a*a);
    }

    public calculator(int a, int b)
    {
        System.out.printf("%d + %d = %d\n",a,b,a+b);
    }

    public static void main(String[] args)
    {
        calculator calc1 = new calculator();
        calculator calc2 = new calculator(10);
        calculator calc4 = new calculator(10,20);
    }

}
