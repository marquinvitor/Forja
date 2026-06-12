```java
import java.util.ArrayList;
import java.util.Scanner;

class Servico {
    String nome;
    double preco;

    public Servico(String nome, double preco) {
        // TODO: inicialize os atributos
    }

    public String getNome() {
        // TODO: retorne o nome do serviço
        return "";
    }

    public double getPreco() {
        // TODO: retorne o preço do serviço
        return 0;
    }

    public void setPreco(double preco) {
        // TODO: altere o preço do serviço
    }

    public String realizarServico() {
        // TODO: implemente este método
        return "";
    }
}

class Banho extends Servico {
    String tipoDeBanho;

    public Banho(String nome, double preco, String tipoDeBanho) {
        super(nome, preco);
        // TODO: inicialize os atributos específicos de Banho
    }

    public String getTipoDeBanho() {
        // TODO: retorne o tipo de banho
        return "";
    }

    public void setTipoDeBanho(String tipoDeBanho) {
        // TODO: altere o tipo de banho
    }

    @Override
    public String realizarServico() {
        // TODO: implemente este método
        return "";
    }
}

class Tosa extends Servico {
    String tipoDeTosa;

    public Tosa(String nome, double preco, String tipoDeTosa) {
        super(nome, preco);
        // TODO: inicialize os atributos específicos de Tosa
    }

    public String getTipoDeTosa() {
        // TODO: retorne o tipo de tosa
        return "";
    }

    public void setTipoDeTosa(String tipoDeTosa) {
        // TODO: altere o tipo de tosa
    }

    @Override
    public String realizarServico() {
        // TODO: implemente este método
        return "";
    }
}

class Consulta extends Servico {
    String especialidade;

    public Consulta(String nome, double preco, String especialidade) {
        super(nome, preco);
        // TODO: inicialize os atributos específicos de Consulta
    }

    public String getEspecialidade() {
        // TODO: retorne a especialidade
        return "";
    }

    public void setEspecialidade(String especialidade) {
        // TODO: altere a especialidade
    }

    @Override
    public String realizarServico() {
        // TODO: implemente este método
        return "";
    }
}

public class Shell {
    static Scanner scanner = new Scanner(System.in);
    static ArrayList<Servico> servicos = new ArrayList<>();

    public static void main(String[] _args) {
        while (true) {
            var line = scanner.nextLine();
            System.out.println("$" + line);
            var par = line.split(" ");
            var cmd = par[0];
            if (cmd.equals("end")) {
                break;
            } else if (cmd.equals("addServico")) {
                var nome = par[1];
                var preco = Double.parseDouble(par[2]);
                if (par[1].equals("banho")) {
                    var tipoDeBanho = par[3];
                    servicos.add(new Banho(nome, preco, tipoDeBanho));
                } else if (par[1].equals("tosa")) {
                    var tipoDeTosa = par[3];
                    servicos.add(new Tosa(nome, preco, tipoDeTosa));
                } else if (par[1].equals("consulta")) {
                    var especialidade = par[3];
                    servicos.add(new Consulta(nome, preco, especialidade));
                }
            } else if (cmd.equals("realizarServicos")) {
                for (Servico s : servicos) {
                    System.out.println(s.realizarServico());
                }
            } else if (cmd.equals("setPreco")) {
                var preco = Double.parseDouble(par[1]);
                if (!servicos.isEmpty()) {
                    servicos.get(servicos.size() - 1).setPreco(preco);
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```