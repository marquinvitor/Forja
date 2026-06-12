import java.util.ArrayList;
import java.util.Scanner;

class Paciente {
    String nome;
    int idade;
    String sexo;
    double altura;
    double peso;
    String[] historicoMedico;

    public Paciente(String nome, int idade, String sexo, double altura, double peso) {
        // TODO: inicialize os atributos
    }

    public String getNome() {
        // TODO: retorne o nome do paciente
        return "";
    }

    public int getIdade() {
        // TODO: retorne a idade do paciente
        return 0;
    }

    public String getSexo() {
        // TODO: retorne o sexo do paciente
        return "";
    }

    public double getAltura() {
        // TODO: retorne a altura do paciente
        return 0;
    }

    public double getPeso() {
        // TODO: retorne o peso do paciente
        return 0;
    }

    public String[] getHistoricoMedico() {
        // TODO: retorne o histórico médico do paciente
        return null;
    }

    public void adicionarHistoricoMedico(String historico) {
        // TODO: adicione um novo histórico médico ao paciente
    }

    public double calcularIMC() {
        // TODO: calcule o índice de massa corporal (IMC) do paciente
        return 0;
    }

    public String getInfo() {
        // TODO: retorne as informações do paciente formatadas
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Paciente> pacientes = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addPaciente")) {
                var nome = par[1];
                var idade = Integer.parseInt(par[2]);
                var sexo = par[3];
                var altura = Double.parseDouble(par[4]);
                var peso = Double.parseDouble(par[5]);
                pacientes.add(new Paciente(nome, idade, sexo, altura, peso));
            } else if (cmd.equals("addHistoricoMedico")) {
                var nome = par[1];
                var historico = par[2];
                for (Paciente p : pacientes) {
                    if (p.getNome().equals(nome)) {
                        p.adicionarHistoricoMedico(historico);
                    }
                }
            } else if (cmd.equals("calcularIMC")) {
                var nome = par[1];
                for (Paciente p : pacientes) {
                    if (p.getNome().equals(nome)) {
                        System.out.println("IMC: " + p.calcularIMC());
                    }
                }
            } else if (cmd.equals("show")) {
                for (Paciente p : pacientes) {
                    System.out.println(p.getInfo());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}