// Practical 5

class Vehicle {
    String brand;
    int year;

    Vehicle(String brand, int year) {
        this.brand = brand;
        this.year = year;
        System.out.println("Vehicle constructor called");
    }

    void displayInfo() {
        System.out.println("Brand: " + brand);
        System.out.println("Year: " + year);
    }
}

class Car extends Vehicle {
    String model;

    Car(String brand,int year, String model) {
        super(brand, year);
        this.model = model;
        System.out.println("Car constructor called");
    }

    void displayInfo() {
        super.displayInfo();
        System.out.println("Year: " + year);
    }
}

public class SingleInh {
    public static void main(String[] args) {
        Car c1 = new Car("Toyota", 2022, "Fortuner");
        c1.displayInfo();
    }
}
