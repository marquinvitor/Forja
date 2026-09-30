import java.util.ArrayList;
import java.util.Scanner;

class Produto {
    String nome;
    float precoUnitario;
    int qtdEmEstoque;

    public Produto(String nome, float preco) {
        // TODO: inicialize os atributos (nome e precoUnitario), qtdEmEstoque começa em 0
    }

    public abstract String getInfo();

    public abstract void vender();

    public int estoqueAtual() {
        return qtdEmEstoque;
    }
}

class Parafuso extends Produto {
    float diametro;
    float comprimento;

    public Parafuso(String nome, float preco, float diametro, float comprimento) {
        super(nome, preco);
        // TODO: inicialize os atributos (diametro e comprimento)
    }

    @Override
    public String getInfo() {
        // TODO: retorne a string formatada conforme o teste esperado
        return "";
    }

    @Override
    public void vender() {
        // TODO: implemente a lógica de validação (d>=3.0 e L>=10.0) e redução de estoque
        System.out.println("fail: dimensões inválidas (d<3.0 ou L<10.0)");
    }
}

class KitFerramental extends Produto {
    ArrayList<String> itens;

    public KitFerramental(String nome, float preco, ArrayList<String> itens) {
        super(nome, preco);
        // TODO: inicialize o atributo (itens) com a lista passada
    }

    @Override
    public String getInfo() {
        // TODO: retorne a string formatada conforme o teste esperado
        return "";
    }

    @Override
    public void vender() {
        // TODO: implemente a lógica de validação (todos itens disponíveis) e redução de estoque
        System.out.println("fail: item indisponível no kit");
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Produto> produtos = new ArrayList<>();
    static Produto ultimoProduto = null;

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];

            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("init")) {
                // Lógica para init Parafuso ou KitFerramental
                String tipo = par[1];
                float preco = Float.parseFloat(par[par.length - 1]);
                
                if (tipo.equals("Parafuso")) {
                    String nome = par[2];
                    float diametro = Float.parseFloat(par[3]);
                    float comprimento = Float.parseFloat(par[4]);
                    ultimoProduto = new Parafuso(nome, preco, diametro, comprimento);
                    produtos.add(ultimoProduto);
                } else if (tipo.equals("KitFerramental")) {
                    String nome = par[2];
                    // Os itens do kit estão entre o índice 3 e penúltimo
                    ArrayList<String> listaItens = new ArrayList<>();
                    for (int i = 3; i < par.length - 1; i++) {
                        listaItens.add(par[i]);
                    }
                    ultimoProduto = new KitFerramental(nome, preco, listaItens);
                    produtos.add(ultimoProduto);
                }
            } else if (cmd.equals("vender")) {
                if (ultimoProduto != null) {
                    ultimoProduto.vender();
                }
            } else if (cmd.equals("show")) {
                if (ultimoProduto != null) {
                    System.out.println(ultimoProduto.getInfo());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}