import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.Locale;

/* ==================== INTERFACES ==================== */
interface Livro {
    String getNome();
    String obterPreco();
}

/* ==================== CLASSES ==================== */
class LivroFisico implements Livro {
    String nome;
    String autor;
    double preco;
    int qtdEstoque;

    public LivroFisico(String nome, String autor, double preco, int qtdEstoque) {
        this.nome = nome;
        this.autor = autor;
        this.preco = preco;
        this.qtdEstoque = qtdEstoque;
    }

    @Override
    public String getNome() {
        return this.nome;
    }

    @Override
    public String obterPreco() {
        // Formata como "R$ 29,90"
        String formatted = String.format(Locale.US, "%.2f", this.preco).replace('.', ',');
        return "R$ " + formatted;
    }
}

class LivroDigital implements Livro {
    String nome;
    String autor;
    double preco;
    String formato;
    int qtdEstoque;

    public LivroDigital(String nome, String autor, double preco, String formato, int qtdEstoque) {
        this.nome = nome;
        this.autor = autor;
        this.preco = preco;
        this.formato = formato;
        this.qtdEstoque = qtdEstoque;
    }

    @Override
    public String getNome() {
        return this.nome;
    }

    @Override
    public String obterPreco() {
        String formatted = String.format(Locale.US, "%.2f", this.preco).replace('.', ',');
        return "R$ " + formatted;
    }
}

/* ==================== CONTROLADORA ==================== */
class Livraria {
    private List<Livro> estoque;

    public Livraria() {
        this.estoque = new ArrayList<>();
    }

    public void adicionarLivro(Livro livro) {
        if (livro instanceof LivroFisico) {
            LivroFisico lf = (LivroFisico) livro;
            if (lf.qtdEstoque > 0) {
                estoque.add(livro);
            }
        } else if (livro instanceof LivroDigital) {
            LivroDigital ld = (LivroDigital) livro;
            if (ld.qtdEstoque > 0) {
                estoque.add(livro);
            }
        }
    }

    public List<String> listarLivros() {
        List<String> nomes = new ArrayList<>();
        for (Livro l : estoque) {
            nomes.add(l.getNome());
        }
        return nomes;
    }
}

/* ==================== SHELL ==================== */
public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static Livraria livraria = new Livraria();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];

            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("add")) {
                // tipo do livro (livroFisico ou livroDigital)
                var tipo = par[1];

                // Extração de nome e autor entre aspas
                int firstQuote = line.indexOf('\"');
                int secondQuote = line.indexOf('\"', firstQuote + 1);
                String nome = line.substring(firstQuote + 1, secondQuote);

                int thirdQuote = line.indexOf('\"', secondQuote + 1);
                int fourthQuote = line.indexOf('\"', thirdQuote + 1);
                String autor = line.substring(thirdQuote + 1, fourthQuote);

                // Parte restante: preço e quantidade
                String after = line.substring(fourthQuote + 1).trim();
                String[] rest = after.split(" ");
                double preco = Double.parseDouble(rest[0]);
                int qtd = Integer.parseInt(rest[1]);

                if (tipo.equals("livroFisico")) {
                    LivroFisico lf = new LivroFisico(nome, autor, preco, qtd);
                    livraria.adicionarLivro(lf);
                } else if (tipo.equals("livroDigital")) {
                    // formato não é informado no comando; usamos string vazia
                    LivroDigital ld = new LivroDigital(nome, autor, preco, "", qtd);
                    livraria.adicionarLivro(ld);
                } else {
                    System.out.println("fail: comando invalido\n");
                }
            } else if (cmd.equals("listarLivros")) {
                List<String> nomes = livraria.listarLivros();
                System.out.print("[ ");
                if (nomes != null) {
                    for (int i = 0; i < nomes.size(); i++) {
                        System.out.print(nomes.get(i));
                        if (i < nomes.size() - 1) System.out.print(" ");
                    }
                }
                System.out.println(" ]");
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}