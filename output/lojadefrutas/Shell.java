import java.util.ArrayList;
import java.util.Scanner;

// ── MODELO DE DOMÍNIO: Loja de Frutas ───────────────────────────────────────

abstract class Produto {
    String nome;
    double precoBase;

    public Produto(String nome, double precoBase) {
        // TODO: inicialize os atributos
    }

    public abstract double precoFinal();

    public String getNome() {
        // TODO: retorne o nome do produto
        return "";
    }
}

class Fruta extends Produto {
    String origem;

    public Fruta(String nome, double precoBase, String origem) {
        super(nome, precoBase);
        // TODO: inicialize os atributos específicos de Fruta
    }

    @Override
    public double precoFinal() {
        // TODO: aplique 5 % de imposto sobre o preço base
        return 0.0;
    }
}

class FrutaExotica extends Fruta {

    public FrutaExotica(String nome, double precoBase, String origem) {
        super(nome, precoBase, origem);
        // TODO: nenhum atributo adicional a inicializar
    }

    @Override
    public double precoFinal() {
        // TODO: aplique 15 % de imposto (5 % + 10 % extra)
        return 0.0;
    }
}

// ── SHELL ───────────────────────────────────────────────────────────────────────

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Produto> estoque = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];

            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("init")) {
                // cria um novo estoque (capacidade opcional)
                int capacidade = Integer.parseInt(par[1]);
                estoque = new ArrayList<>(capacidade);
            } else if (cmd.equals("addFruit")) {
                var nome = par[1];
                var precoBase = Double.parseDouble(par[2]);
                var origem = par[3];
                estoque.add(new Fruta(nome, precoBase, origem));
            } else if (cmd.equals("addExotic")) {
                var nome = par[1];
                var precoBase = Double.parseDouble(par[2]);
                var origem = par[3];
                estoque.add(new FrutaExotica(nome, precoBase, origem));
            } else if (cmd.equals("show")) {
                for (Produto p : estoque) {
                    StringBuilder sb = new StringBuilder();
                    sb.append(p.getNome()).append(" ");
                    sb.append(String.format("%.2f", p.precoFinal()));
                    if (p instanceof Fruta) {
                        sb.append(" ").append(((Fruta) p).origem);
                    }
                    System.out.println(sb.toString());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}