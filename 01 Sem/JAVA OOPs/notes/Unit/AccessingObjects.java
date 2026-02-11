// Demonstrate the procedure for creating and accessing objects in Java

class Car {

    String brand;
    int speed;

    void display() {
        System.out.println("Brand: " + brand);
        System.out.println("Speed: " + speed + "Km");
    }
}

public class AccessingObjects {
    public static void main(String[] args) {

        Car c1 = new Car();   // Object creation
        c1.brand = "BMW";     // Accessing variables
        c1.speed = 120;
        // c1.display();         // Calling method

        Car Baleno = new Car();
        Baleno.brand = "Suzuki";
        Baleno.speed = 90;

        Car dodgeChallanger = new Car();
        dodgeChallanger.brand = "Dodge";
        dodgeChallanger.speed = 300;

        // Baleno.display();
        dodgeChallanger.display();
    }
}
