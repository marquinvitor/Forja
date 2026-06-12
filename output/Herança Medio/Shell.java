```java
import java.util.ArrayList;
import java.util.Scanner;

class Item {
    String titulo;
    String autor;
    int anoPublicacao;
    int quantidadeEstoque;

    public Item(String titulo, String autor, int anoPublicacao, int quantidadeEstoque) {
        // TODO: inicialize os atributos
    }

    public double getValorTotal() {
        // TODO: implemente este método
        return 0;
    }

    @Override
    public String toString() {
        // TODO: implemente este método
        return "";
    }
}

class Livro extends Item {
    double preco;

    public Livro(String titulo, String autor, int anoPublicacao, int quantidadeEstoque) {
        super(titulo, autor, anoPublicacao, quantidadeEstoque);
        // TODO: inicialize os atributos específicos de Livro
    }

    @Override
    public double getValorTotal() {
        // TODO: implemente este método
        return 0;
    }

    @Override
    public String toString() {
        // TODO: implemente este método
        return "";
    }
}

class Revista extends Item {
    double preco;

    public Revista(String titulo, String autor, int anoPublicacao, int quantidadeEstoque) {
        super(titulo, autor, anoPublicacao, quantidadeEstoque);
        // TODO: inicialize os atributos específicos de Revista
    }

    @Override
    public double getValorTotal() {
        // TODO: implemente este método
        return 0;
    }

    @Override
    public String toString() {
        // TODO: implemente este método
        return "";
    }
}

class CD extends Item {
    double preco;

    public CD(String titulo, String autor, int anoPublicacao, int quantidadeEstoque) {
        super(titulo, autor, anoPublicacao, quantidadeEstoque);
        // TODO: inicialize os atributos específicos de CD
    }

    @Override
    public double getValorTotal() {
        // TODO: implemente este método
        return 0;
    }

    @Override
    public String toString() {
        // TODO: implemente este método
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Item> itens = new ArrayList<>();

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
                var titulo = par[2];
                var autor = par[3];
                var anoPublicacao = Integer.parseInt(par[4]);
                var quantidadeEstoque = Integer.parseInt(par[5]);
                if (tipo.equals("Livro")) {
                    itens.add(new Livro(titulo, autor, anoPublicacao, quantidadeEstoque));
                } else if (tipo.equals("Revista")) {
                    itens.add(new Revista(titulo, autor, anoPublicacao, quantidadeEstoque));
                } else if (tipo.equals("CD")) {
                    itens.add(new CD(titulo, autor, anoPublicacao, quantidadeEstoque));
                }
            } else if (cmd.equals("show")) {
                for (Item item : itens) {
                    System.out.println(item.toString());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```