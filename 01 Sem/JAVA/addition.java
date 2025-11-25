import java.util.Scanner;

class addition{
    public static void main(String[] args)
    {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter a number = ");
        int a = sc.nextInt();

        System.out.print("Enter a number = ");
        int b = sc.nextInt();

        int ans = a + b;
        System.out.println(a + " + " + b + " = " + ans);

        sc.close();
    }
}