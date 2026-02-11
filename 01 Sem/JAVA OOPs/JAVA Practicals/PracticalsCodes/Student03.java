// practical 3 : encapsulation

public class Student03 {
    private String name;
    private int roll;
    private String year;

    public Student03(String name, int roll, String year)
    {
        this.name = name;
        this.roll = roll;
        this.year = year;
    }

    public String getName()
    {
        return this.name;
    }

    public int getRoll()
    {
        return this.roll;
    }

    public String getYear()
    {
        return this.year;
    }

    public void setName(String name)
    {
        this.name = name;
    }

    public void setRoll(int roll)
    {
        this.roll = roll;
    }

    public void setYear(String year)
    {
        this.year = year;
    }

    public static void main(String[] args)
    {
        Student03 Premraj = new Student03("Prem", 101, "1st year");
        System.out.println("Given Data");
        System.out.println("name = "+Premraj.getName());
        System.out.println("roll = "+Premraj.getRoll());
        System.out.println("year = "+Premraj.getYear());

        Premraj.setName("Prajwal");
        Premraj.setRoll(10001);
        Premraj.setYear("2nd year");

        System.out.println("\nUpdated Data");
        System.out.println("name = "+Premraj.getName());
        System.out.println("roll = "+Premraj.getRoll());
        System.out.println("year = "+Premraj.getYear());

    }
}



