import java.util.ArrayList;
import java.util.Scanner;

// ── CONTEXTO: loja de móveis ───────────────────────────────────────────────

abstract class Produto {
    String nome;
    double precoBase;

    public Produto(String nome, double precoBase) {
        // TODO: inicialize os atributos
    }

    public abstract double calcularPrecoFinal();

    public String getNome() {
        // TODO: retorne o nome
        return "";
    }

    public double getPrecoBase() {
        // TODO: retorne o preço base
        return 0;
    }
}

class Cadeira extends Produto {
    String material;

    public Cadeira(String nome, double precoBase, String material) {
        super(nome, precoBase);
        // TODO: inicialize os atributos específicos de Cadeira
    }

    @Override
    public double calcularPrecoFinal() {
        // TODO: implemente o cálculo do preço final da cadeira
        return 0;
    }
}

class Mesa extends Produto {
    String forma;

    public Mesa(String nome, double precoBase, String forma) {
        super(nome, precoBase);
        // TODO: inicialize os atributos específicos de Mesa
    }

    @Override
    public double calcularPrecoFinal() {
        // TODO: implemente o cálculo do preço final da mesa
        return 0;
    }
}

class Sofa extends Produto {
    int capacidade;

    public Sofa(String nome, double precoBase, int capacidade) {
        super(nome, precoBase);
        // TODO: inicialize os atributos específicos de Sofa
    }

    @Override
    public double calcularPrecoFinal() {
        // TODO: implemente o cálculo do preço final do sofá
        return 0;
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
                var tipo = par[1];
                var nome = par[2];
                var preco = Double.parseDouble(par[3]);

                if (tipo.equals("cadeira")) {
                    var material = par[4];
                    produtos.add(new Cadeira(nome, preco, material));
                } else if (tipo.equals("mesa")) {
                    var forma = par[4];
                    produtos.add(new Mesa(nome, preco, forma));
                } else if (tipo.equals("sofa")) {
                    var capacidade = Integer.parseInt(par[4]);
                    produtos.add(new Sofa(nome, preco, capacidade));
                } else {
                    System.out.println("fail: comando invalido\n");
                }
            } else if (cmd.equals("show")) {
                for (Produto p : produtos) {
                    if (p instanceof Cadeira) {
                        Cadeira c = (Cadeira) p;
                        System.out.println("cadeira " + c.nome + " " + c.precoBase + " " + c.material);
                    } else if (p instanceof Mesa) {
                        Mesa m = (Mesa) p;
                        System.out.println("mesa " + m.nome + " " + m.precoBase + " " + m.forma);
                    } else if (p instanceof Sofa) {
                        Sofa s = (Sofa) p;
                        System.out.println("sofa " + s.nome + " " + s.precoBase + " " + s.capacidade);
                    }
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}