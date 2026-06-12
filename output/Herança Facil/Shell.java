```java
import java.util.ArrayList;
import java.util.Scanner;

class Veiculo {
    String marca;
    String modelo;
    int ano;

    public Veiculo(String marca, String modelo, int ano) {
        // TODO: inicialize os atributos
    }

    public String imprimirInformacoes() {
        // TODO: implemente este método
        return "";
    }
}

class Aviao extends Veiculo {
    int capacidadePassageiros;
    int altitudeMaxima;

    public Aviao(String marca, String modelo, int ano, int capacidadePassageiros, int altitudeMaxima) {
        super(marca, modelo, ano);
        // TODO: inicialize os atributos específicos de Aviao
    }

    public String imprimirInformacoesAviao() {
        // TODO: implemente este método
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Veiculo> veiculos = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addVeiculo")) {
                var marca = par[1];
                var modelo = par[2];
                var ano = Integer.parseInt(par[3]);
                veiculos.add(new Veiculo(marca, modelo, ano));
            } else if (cmd.equals("addAviao")) {
                var marca = par[1];
                var modelo = par[2];
                var ano = Integer.parseInt(par[3]);
                var capacidadePassageiros = Integer.parseInt(par[4]);
                var altitudeMaxima = Integer.parseInt(par[5]);
                veiculos.add(new Aviao(marca, modelo, ano, capacidadePassageiros, altitudeMaxima));
            } else if (cmd.equals("show")) {
                for (Veiculo v : veiculos) {
                    if (v instanceof Aviao) {
                        System.out.println(((Aviao) v).imprimirInformacoesAviao());
                    } else {
                        System.out.println(v.imprimirInformacoes());
                    }
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```