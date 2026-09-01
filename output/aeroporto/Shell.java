
import java.util.ArrayList;
import java.util.Scanner;

class Funcionario {
    String nome;
    int idade;
    int matricula;

    public Funcionario(String nome, int idade, int matricula) {
        // TODO: inicialize os atributos
    }

    public String exibirInfo() {
        // TODO: retorne as informações do funcionário formatadas
        return "";
    }
}

class Piloto extends Funcionario {
    int horasVoo;

    public Piloto(String nome, int idade, int matricula, int horasVoo) {
        super(nome, idade, matricula);
        // TODO: inicialize os atributos específicos de Piloto
    }

    @Override
    public String exibirInfo() {
        // TODO: retorne as informações do piloto, incluindo o número de horas de voo
        return "";
    }
}

class Comissario extends Funcionario {
    String[] linguas;

    public Comissario(String nome, int idade, int matricula, String[] linguas) {
        super(nome, idade, matricula);
        // TODO: inicialize os atributos específicos de Comissario
    }

    @Override
    public String exibirInfo() {
        // TODO: retorne as informações do comissário, incluindo as línguas que fala
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Funcionario> funcionarios = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("criarFuncionario")) {
                var nome = par[1];
                var idade = Integer.parseInt(par[2]);
                var matricula = Integer.parseInt(par[3]);
                funcionarios.add(new Funcionario(nome, idade, matricula));
            } else if (cmd.equals("criarPiloto")) {
                var nome = par[1];
                var idade = Integer.parseInt(par[2]);
                var matricula = Integer.parseInt(par[3]);
                var horasVoo = Integer.parseInt(par[4]);
                funcionarios.add(new Piloto(nome, idade, matricula, horasVoo));
            } else if (cmd.equals("criarComissario")) {
                var nome = par[1];
                var idade = Integer.parseInt(par[2]);
                var matricula = Integer.parseInt(par[3]);
                var linguas = new String[par.length - 4];
                for (int i = 4; i < par.length; i++) {
                    linguas[i - 4] = par[i];
                }
                funcionarios.add(new Comissario(nome, idade, matricula, linguas));
            } else if (cmd.equals("exibirInfo")) {
                var matricula = Integer.parseInt(par[1]);
                for (Funcionario f : funcionarios) {
                    if (f.matricula == matricula) {
                        System.out.println(f.exibirInfo());
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