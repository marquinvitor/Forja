```java
import java.util.ArrayList;
import java.util.Scanner;

class Ferramenta {
    String nome;
    double preco;
    String descricao;

    public Ferramenta(String nome, double preco, String descricao) {
        // TODO: inicialize os atributos
    }

    public String getInfo() {
        // TODO: retorne as informações da ferramenta formatadas
        return "";
    }

    public double getImposto() {
        // TODO: retorne o imposto da ferramenta
        return 0;
    }
}

class Martelo extends Ferramenta {
    double peso;

    public Martelo(String nome, double preco, String descricao, double peso) {
        super(nome, preco, descricao);
        // TODO: inicialize os atributos específicos de Martelo
    }

    @Override
    public String getInfo() {
        // TODO: retorne as informações completas do martelo
        return "";
    }

    @Override
    public double getImposto() {
        // TODO: retorne o imposto do martelo
        return 0;
    }
}

class Serrote extends Ferramenta {
    double comprimentoLamina;

    public Serrote(String nome, double preco, String descricao, double comprimentoLamina) {
        super(nome, preco, descricao);
        // TODO: inicialize os atributos específicos de Serrote
    }

    @Override
    public String getInfo() {
        // TODO: retorne as informações completas do serrote
        return "";
    }

    @Override
    public double getImposto() {
        // TODO: retorne o imposto do serrote
        return 0;
    }
}

class ChaveDeFenda extends Ferramenta {
    int tamanho;

    public ChaveDeFenda(String nome, double preco, String descricao, int tamanho) {
        super(nome, preco, descricao);
        // TODO: inicialize os atributos específicos de ChaveDeFenda
    }

    @Override
    public String getInfo() {
        // TODO: retorne as informações completas da chave de fenda
        return "";
    }

    @Override
    public double getImposto() {
        // TODO: retorne o imposto da chave de fenda
        return 0;
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Ferramenta> ferramentas = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addItem")) {
                var nome = par[1];
                var preco = Double.parseDouble(par[2]);
                var descricao = "";
                if (par[3].equals("Martelo")) {
                    var peso = Double.parseDouble(par[4]);
                    ferramentas.add(new Martelo(nome, preco, descricao, peso));
                } else if (par[3].equals("Serrote")) {
                    var comprimentoLamina = Double.parseDouble(par[4]);
                    ferramentas.add(new Serrote(nome, preco, descricao, comprimentoLamina));
                } else if (par[3].equals("ChaveDeFenda")) {
                    var tamanho = Integer.parseInt(par[4]);
                    ferramentas.add(new ChaveDeFenda(nome, preco, descricao, tamanho));
                }
            } else if (cmd.equals("show")) {
                for (Ferramenta f : ferramentas) {
                    System.out.println(f.getInfo());
                    System.out.println("Imposto: R$ " + f.getImposto());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```