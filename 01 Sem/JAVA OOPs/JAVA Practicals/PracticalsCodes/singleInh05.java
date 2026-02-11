// practical 5: single inheritance
class vehicle{
    String brand;
    int year;
    vehicle(String brand, int year)
    {
        this.brand = brand;
        this.year = year;
    }

    public void displayInfo()
    {
        System.out.println("brand = "+this.brand);
        System.out.println("year = "+this.year);
    }
}

class Car extends vehicle
{
    String model;
    public Car(String brand, int year, String model)
    {
        super(brand,year);
        this.model = model;
    }

    public void displayInfo()
    {
        super.displayInfo();
        System.out.println("model = "+this.model);
    }
}


public class singleInh05 {
    public static void main(String[] args)
    {
        Car nano = new Car("Tata", 2010, "nano");
        nano.displayInfo();
    }
    
}
