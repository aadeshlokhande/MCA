import java.io.*;
import java.util.*;

public class QuizApp {
    static class Question {
        String number, text;
        String[] opts = new String[4];
        char answer; // 'a'..'d'

        Question(String number, String text, String a, String b, String c, String d, String ans) {
            this.number = number;
            this.text = text;
            opts[0] = a;
            opts[1] = b;
            opts[2] = c;
            opts[3] = d;
            answer = (ans == null || ans.isEmpty()) ? '?' : Character.toLowerCase(ans.trim().charAt(0));
        }
    }

    public static List<Question> loadFromCSV(String path) {
        List<Question> list = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) continue;
                // naive split - assumes no commas inside fields
                String[] parts = line.split(",", -1);
                // detect header row like: question number,question,...
                if (parts.length >= 2 && parts[0].toLowerCase().contains("question") && parts[1].toLowerCase().contains("question")) {
                    continue;
                }
                if (parts.length < 7) {
                    System.err.println("Skipping malformed line: " + line);
                    continue;
                }
                Question q = new Question(parts[0].trim(), parts[1].trim(),
                        parts[2].trim(), parts[3].trim(), parts[4].trim(), parts[5].trim(),
                        parts[6].trim());
                list.add(q);
            }
        } catch (FileNotFoundException e) {
            System.err.println("CSV file not found: " + path);
        } catch (IOException e) {
            System.err.println("Error reading CSV: " + e.getMessage());
        }
        return list;
    }

    public static void main(String[] args) {
        String path = (args.length > 0) ? args[0] : "questions.csv";
        List<Question> questions = loadFromCSV(path);
        if (questions.isEmpty()) {
            System.out.println("Koi valid question nahi mila. CSV check karo: " + path);
            return;
        }

        Scanner sc = new Scanner(System.in);
        int correct = 0;
        int qnum = 0;
        for (Question q : questions) {
            qnum++;
            System.out.println();
            System.out.println("Q" + qnum + ": " + q.text);
            System.out.println("a) " + q.opts[0]);
            System.out.println("b) " + q.opts[1]);
            System.out.println("c) " + q.opts[2]);
            System.out.println("d) " + q.opts[3]);

            char userAns = '?';
            while (true) {
                System.out.print("Your answer (a/b/c/d): ");
                String input = sc.nextLine().trim().toLowerCase();
                if (input.isEmpty()) continue;
                char ch = input.charAt(0);
                if (ch >= 'a' && ch <= 'd') {
                    userAns = ch;
                    break;
                }
                // also allow 1-4
                if (input.charAt(0) >= '1' && input.charAt(0) <= '4') {
                    userAns = (char) ('a' + (input.charAt(0) - '1'));
                    break;
                }
                System.out.println("Invalid input. Enter a, b, c, d or 1-4.");
            }

            if (userAns == q.answer) {
                System.out.println("Correct!");
                correct++;
            } else {
                System.out.println("Wrong! Correct answer: " + q.answer);
            }
        }

        System.out.println();
        System.out.println("Quiz complete.");
        System.out.printf("Score: %d out of %d (%.2f%%)%n", correct, questions.size(),
                (questions.size() == 0 ? 0.0 : (correct * 100.0 / questions.size())));
        
        sc.close();
    }

}
