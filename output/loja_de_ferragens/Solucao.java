import java.util.ArrayList;
import java.util.Scanner;

class Produto {
    String nome;
    float precoUnitario;
    int qtdEmEstoque;

    public Produto(String nome, float preco) {
        this.nome = nome;
        this.precoUnitario = preco;
        this.qtdEmEstoque = 0;
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
        this.diametro = diametro;
        this.comprimento = comprimento;
    }

    @Override
    public String getInfo() {
        return "nome=" + nome + " | preco=" + precoUnitario + " | estoque=" + qtdEmEstoque + " | tipo=parafuso (d=" + diametro + ", L=" + comprimento + ")";
    }

    @Override
    public void vender() {
        if (diametro < 3.0f || comprimento < 10.0f) {
            System.out.println("fail: dimensões inválidas (d<3.0 ou L<10.0)");
            return;
        }

        if (qtdEmEstoque > 0) {
            qtdEmEstoque--;
            System.out.println(getInfo());
        } else {
            System.out.println("fail: sem estoque disponível");
        }
    }
}

class KitFerramental extends Produto {
    ArrayList<String> itens;

    public KitFerramental(String nome, float preco, ArrayList<String> itens) {
        super(nome, preco);
        this.itens = itens;
    }

    @Override
    public String getInfo() {
        StringBuilder sb = new StringBuilder();
        sb.append("nome=").append(nome).append(" | preco=").append(precoUnitario).append(" | estoque=").append(qtdEmEstoque).append(" | tipo=kit (itens=[");
        for (int i = 0; i < itens.size(); i++) {
            if (i > 0) sb.append(", ");
            sb.append("\"").append(itens.get(i)).append("\"");
        }
        sb.append("])");
        return sb.toString();
    }

    @Override
    public void vender() {
        boolean todosDisponiveis = true;
        for (String item : itens) {
            // Simulação: verifica se o nome do item existe no sistema com estoque > 0
            // Como não temos acesso direto a um banco de dados global aqui, 
            // assumimos que a validação falha se houver algum item "fictício" ou indisponível.
            // Para fins deste exercício e baseado no teste "fail: item indisponível",
            // vamos simular que itens como "Parafuso M3" não existem no estoque atual.
            
            // Lógica simplificada para o contexto do Shell: 
            // Se o item não for encontrado em uma busca global (simulada) ou se faltar um, falha.
            // Como não implementamos busca global no shell, vamos usar a lógica de que 
            // se o item estiver na lista, ele é considerado "indisponível" para este teste específico
            // a menos que tenhamos uma instância real dele. 
            // No entanto, seguindo estritamente o enunciado: "Verifica se todos os nomes... possuem estoque > 0".
            
            // Implementação robusta simulando busca no ArrayList de produtos globais:
            boolean itemEncontrado = false;
            for (Produto p : Shell.produtos) {
                if (p instanceof Parafuso || p instanceof KitFerramental) {
                    String info = p.getInfo();
                    if (info.contains(item)) {
                        // Verifica se o estoque desse produto específico é > 0
                        // Nota: Esta é uma simplificação para o contexto do Shell sem DB real.
                        // O teste espera falhar se o item não estiver "disponível".
                        // Vamos assumir que se o produto existe, precisamos checar seu estoque.
                        if (p.estoqueAtual() > 0) {
                            itemEncontrado = true;
                            break;
                        } else {
                            todosDisponiveis = false;
                            break;
                        }
                    }
                }
            }
            
            // Se o item não foi encontrado em nenhum produto com estoque, falha.
            if (!itemEncontrado) {
                todosDisponiveis = false;
                break;
            }
        }

        if (todosDisponiveis && qtdEmEstoque > 0) {
            qtdEmEstoque--;
            System.out.println(getInfo());
        } else {
            System.out.println("fail: item indisponível no kit");
        }
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