```java
import java.util.ArrayList;
import java.util.Scanner;

class Aluno {
    private String nome;
    private String matricula;
    private double nota1;
    private double nota2;

    public Aluno(String nome, String matricula, double nota1, double nota2) {
        // TODO: inicialize os atributos
    }

    public String getNome() {
        // TODO: implemente este método
        return "";
    }

    public String getMatricula() {
        // TODO: implemente este método
        return "";
    }

    public double getNota1() {
        // TODO: implemente este método
        return 0;
    }

    public double getNota2() {
        // TODO: implemente este método
        return 0;
    }

    public double calculaMedia() {
        // TODO: implemente este método
        return 0;
    }

    public boolean isAprovado() {
        // TODO: implemente este método
        return false;
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Aluno> alunos = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addAluno")) {
                var nome = par[1];
                var matricula = par[2];
                var nota1 = Double.parseDouble(par[3]);
                var nota2 = Double.parseDouble(par[4]);
                alunos.add(new Aluno(nome, matricula, nota1, nota2));
            } else if (cmd.equals("show")) {
                for (Aluno a : alunos) {
                    System.out.println(a.getNome() + " " + a.getMatricula() + " " + a.getNota1() + " " + a.getNota2());
                }
            } else if (cmd.equals("media")) {
                var nome = par[1];
                for (Aluno a : alunos) {
                    if (a.getNome().equals(nome)) {
                        System.out.println(a.calculaMedia());
                        break;
                    }
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```