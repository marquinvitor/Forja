```java
import java.util.ArrayList;
import java.util.Scanner;

class ContaBancaria {
    int numeroConta;
    double saldo;
    String nomeTitular;

    public ContaBancaria(int numeroConta, double saldo, String nomeTitular) {
        // TODO: inicialize os atributos
    }

    public void depositar(double valor) {
        // TODO: implemente este método
    }

    public void sacar(double valor) {
        // TODO: implemente este método
    }

    public double getSaldo() {
        // TODO: implemente este método
        return 0;
    }

    public String getNomeTitular() {
        // TODO: implemente este método
        return "";
    }

    public String getInfo() {
        // TODO: implemente este método
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<ContaBancaria> contas = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addConta")) {
                var numeroConta = Integer.parseInt(par[1]);
                var saldo = Double.parseDouble(par[2]);
                var nomeTitular = par[3];
                contas.add(new ContaBancaria(numeroConta, saldo, nomeTitular));
            } else if (cmd.equals("depositar")) {
                var numeroConta = Integer.parseInt(par[1]);
                var valor = Double.parseDouble(par[2]);
                for (ContaBancaria conta : contas) {
                    if (conta.numeroConta == numeroConta) {
                        conta.depositar(valor);
                    }
                }
            } else if (cmd.equals("sacar")) {
                var numeroConta = Integer.parseInt(par[1]);
                var valor = Double.parseDouble(par[2]);
                for (ContaBancaria conta : contas) {
                    if (conta.numeroConta == numeroConta) {
                        conta.sacar(valor);
                    }
                }
            } else if (cmd.equals("show")) {
                for (ContaBancaria conta : contas) {
                    System.out.println(conta.getInfo());
                }
            } else if (cmd.equals("getNomeTitular")) {
                var numeroConta = Integer.parseInt(par[1]);
                for (ContaBancaria conta : contas) {
                    if (conta.numeroConta == numeroConta) {
                        System.out.println(conta.getNomeTitular());
                    }
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```