```java
import java.util.ArrayList;
import java.util.Scanner;

class Produto {
    String codigo;
    String nome;
    double preco;
    int quantidadeEstoque;

    public Produto(String codigo, String nome, double preco, int quantidadeEstoque) {
        // TODO: inicialize os atributos
    }

    public double calcularValorTotalEstoque() {
        // TODO: implemente este método
        return 0;
    }

    public boolean verificarEstoque() {
        // TODO: implemente este método
        return false;
    }

    public String getInfo() {
        // TODO: implemente este método
        return "";
    }
}

class Alimento extends Produto {
    String dataValidade;

    public Alimento(String codigo, String nome, double preco, int quantidadeEstoque, String dataValidade) {
        super(codigo, nome, preco, quantidadeEstoque);
        // TODO: inicialize os atributos específicos de Alimento
    }

    public boolean verificarValidade() {
        // TODO: implemente este método
        return false;
    }

    @Override
    public String getInfo() {
        // TODO: implemente este método
        return "";
    }
}

class ProdutoLimpeza extends Produto {
    String tipoLimpeza;

    public ProdutoLimpeza(String codigo, String nome, double preco, int quantidadeEstoque, String tipoLimpeza) {
        super(codigo, nome, preco, quantidadeEstoque);
        // TODO: inicialize os atributos específicos de ProdutoLimpeza
    }

    public boolean verificarTipoLimpeza() {
        // TODO: implemente este método
        return false;
    }

    @Override
    public String getInfo() {
        // TODO: implemente este método
        return "";
    }
}

class Eletronico extends Produto {
    String modelo;
    String marca;

    public Eletronico(String codigo, String nome, double preco, int quantidadeEstoque, String marca, String modelo) {
        super(codigo, nome, preco, quantidadeEstoque);
        // TODO: inicialize os atributos específicos de Eletronico
    }

    public boolean verificarGarantia() {
        // TODO: implemente este método
        return false;
    }

    @Override
    public String getInfo() {
        // TODO: implemente este método
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Produto> produtos = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addItem")) {
                if (par[4].matches("\\d{4}-\\d{2}-\\d{2}")) {
                    var codigo = par[1];
                    var nome = par[2];
                    var preco = Double.parseDouble(par[3]);
                    var quantidadeEstoque = Integer.parseInt(par[4].split("-")[0]);
                    var dataValidade = par[4];
                    produtos.add(new Alimento(codigo, nome, preco, quantidadeEstoque, dataValidade));
                } else if (par.length == 6) {
                    var codigo = par[1];
                    var nome = par[2];
                    var preco = Double.parseDouble(par[3]);
                    var quantidadeEstoque = Integer.parseInt(par[4]);
                    var marca = par[5].split(" ")[0];
                    var modelo = par[5].split(" ")[1];
                    produtos.add(new Eletronico(codigo, nome, preco, quantidadeEstoque, marca, modelo));
                } else {
                    var codigo = par[1];
                    var nome = par[2];
                    var preco = Double.parseDouble(par[3]);
                    var quantidadeEstoque = Integer.parseInt(par[4]);
                    var tipoLimpeza = par[5];
                    produtos.add(new ProdutoLimpeza(codigo, nome, preco, quantidadeEstoque, tipoLimpeza));
                }
            } else if (cmd.equals("show")) {
                for (Produto p : produtos) {
                    System.out.println(p.getInfo());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```