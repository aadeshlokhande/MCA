import java.io.*;
import java.util.*;

public class QuizApp {

    // Inner class for Question
    static class Question {
        String number;
        String text;
        String[] opts = new String[4];
        char answer; // a, b, c, d

        Question(String number, String text, String a, String b, String c, String d, String ans) {
            this.number = number;
            this.text = text;
            this.opts[0] = a;
            this.opts[1] = b;
            this.opts[2] = c;
            this.opts[3] = d;
            this.answer = (ans == null || ans.isEmpty())
                    ? '?'
                    : Character.toLowerCase(ans.trim().charAt(0));
        }
    }

    // CSV se questions load karne ka method
    public static List<Question> loadFromCSV(String path) {
        List<Question> list = new ArrayList<>();

        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) continue;

                String[] parts = line.split(",", -1);

                // Header skip (optional)
                if (parts.length >= 2 &&
                        parts[0].toLowerCase().contains("question") &&
                        parts[1].toLowerCase().contains("question")) {
                    continue;
                }

                if (parts.length < 7) {
                    System.err.println("Skipping malformed line: " + line);
                    continue;
                }

                Question q = new Question(
                        parts[0].trim(),
                        parts[1].trim(),
                        parts[2].trim(),
                        parts[3].trim(),
                        parts[4].trim(),
                        parts[5].trim(),
                        parts[6].trim()
                );
                list.add(q);
            }
        } catch (FileNotFoundException e) {
            System.err.println("CSV file not found: " + path);
        } catch (IOException e) {
            System.err.println("Error reading CSV: " + e.getMessage());
        }

        return list;
    }

    // Main menu
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (true) {
            System.out.println("\n===== QUIZ MENU =====");
            System.out.println("1. Start Quiz");
            System.out.println("2. View Scoreboard");
            System.out.println("3. Exit");
            System.out.print("Enter your choice: ");

            String choiceStr = sc.nextLine().trim();
            int choice;
            try {
                choice = Integer.parseInt(choiceStr);
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter 1, 2 or 3.");
                continue;
            }

            if (choice == 1) {
                startQuiz(sc);
            } else if (choice == 2) {
                viewScoreboard();
            } else if (choice == 3) {
                System.out.println("Thank you for using the Quiz App.");
                break;
            } else {
                System.out.println("Invalid choice. Try again.");
            }
        }

        sc.close();
    }

    // Quiz start function
    public static void startQuiz(Scanner sc) {
        System.out.print("Enter Student Name: ");
        String studentName = sc.nextLine().trim();

        System.out.print("Enter Roll Number: ");
        String roll = sc.nextLine().trim();

        List<Question> questions = loadFromCSV("questions.csv");

        if (questions.isEmpty()) {
            System.out.println("No questions found. Please check questions.csv");
            return;
        }

        int correct = 0;
        int qnum = 0;

        for (Question q : questions) {
            qnum++;
            System.out.println("\nQ" + qnum + ": " + q.text);
            System.out.println("a) " + q.opts[0]);
            System.out.println("b) " + q.opts[1]);
            System.out.println("c) " + q.opts[2]);
            System.out.println("d) " + q.opts[3]);

            char userAns;

            while (true) {
                System.out.print("Your answer (a/b/c/d): ");
                String input = sc.nextLine().trim().toLowerCase();
                if (!input.isEmpty()) {
                    char ch = input.charAt(0);
                    if (ch >= 'a' && ch <= 'd') {
                        userAns = ch;
                        break;
                    }
                }
                System.out.println("Invalid input. Please enter a, b, c or d.");
            }

            if (userAns == q.answer) {
                System.out.println("Correct!");
                correct++;
            } else {
                System.out.println("Wrong! Correct answer: " + q.answer);
            }
        }

        int total = questions.size();
        double percentage = (correct * 100.0) / total;

        System.out.println("\n===== RESULT =====");
        System.out.println("Roll Number : " + roll);
        System.out.println("Student Name: " + studentName);
        System.out.println("Score       : " + correct + " / " + total);
        System.out.printf("Percentage  : %.2f%%\n", percentage);

        saveMarksheet(roll, studentName, correct, total);
    }

    // Result ko marksheet.csv me save karne ka function
    public static void saveMarksheet(String roll, String name, int score, int total) {
        String fileName = "marksheet.csv";

        try (FileWriter fw = new FileWriter(fileName, true)) {
            File file = new File(fileName);

            if (!file.exists() || file.length() == 0) {
                fw.write("Roll Number,Student Name,Score,Total,Percentage\n");
            }

            double percent = (score * 100.0) / total;
            fw.write(roll + "," + name + "," + score + "," + total + "," +
                    String.format("%.2f", percent) + "\n");

            System.out.println("Result saved to " + fileName);
        } catch (IOException e) {
            System.out.println("Error writing marksheet: " + e.getMessage());
        }
    }

    // Scoreboard view karne ka function
    public static void viewScoreboard() {
        String fileName = "marksheet.csv";
        System.out.println("\n===== SCOREBOARD =====");

        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            boolean any = false;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
                any = true;
            }
            if (!any) {
                System.out.println("Scoreboard empty. No results found.");
            }
        } catch (FileNotFoundException e) {
            System.out.println("Scoreboard empty. " + fileName + " not found.");
        } catch (IOException e) {
            System.out.println("Error reading scoreboard: " + e.getMessage());
        }
    }
}
