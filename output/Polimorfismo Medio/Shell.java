```java
import java.util.ArrayList;
import java.util.Scanner;

class Veiculo {
    String placa;
    String tipo;
    double tempoPermanencia;

    public Veiculo(String placa, String tipo, double tempoPermanencia) {
        // TODO: inicialize os atributos
    }

    public String getPlaca() {
        // TODO: retorne a placa do veículo
        return "";
    }

    public String getTipo() {
        // TODO: retorne o tipo do veículo
        return "";
    }

    public double getTempoPermanencia() {
        // TODO: retorne o tempo de permanência do veículo
        return 0;
    }

    public double calculaEstadia() {
        // TODO: calcule o valor da estadia do veículo
        return 0;
    }
}

class Carro extends Veiculo {
    public Carro(String placa, double tempoPermanencia) {
        super(placa, "Carro", tempoPermanencia);
        // TODO: inicialize os atributos específicos de Carro
    }

    @Override
    public double calculaEstadia() {
        // TODO: calcule o valor da estadia do Carro
        return 0;
    }
}

class Moto extends Veiculo {
    public Moto(String placa, double tempoPermanencia) {
        super(placa, "Moto", tempoPermanencia);
        // TODO: inicialize os atributos específicos de Moto
    }

    @Override
    public double calculaEstadia() {
        // TODO: calcule o valor da estadia da Moto
        return 0;
    }
}

class Caminhao extends Veiculo {
    public Caminhao(String placa, double tempoPermanencia) {
        super(placa, "Caminhao", tempoPermanencia);
        // TODO: inicialize os atributos específicos de Caminhao
    }

    @Override
    public double calculaEstadia() {
        // TODO: calcule o valor da estadia do Caminhao
        return 0;
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
            } else if (cmd.equals("addCarro")) {
                var placa = par[1];
                var tempoPermanencia = Double.parseDouble(par[2]);
                if (tempoPermanencia % 60 == 0) {
                    tempoPermanencia /= 60;
                }
                veiculos.add(new Carro(placa, tempoPermanencia));
            } else if (cmd.equals("addMoto")) {
                var placa = par[1];
                var tempoPermanencia = Double.parseDouble(par[2]);
                if (tempoPermanencia % 60 == 0) {
                    tempoPermanencia /= 60;
                }
                veiculos.add(new Moto(placa, tempoPermanencia));
            } else if (cmd.equals("addCaminhao")) {
                var placa = par[1];
                var tempoPermanencia = Double.parseDouble(par[2]);
                if (tempoPermanencia % 60 == 0) {
                    tempoPermanencia /= 60;
                }
                veiculos.add(new Caminhao(placa, tempoPermanencia));
            } else if (cmd.equals("show")) {
                for (Veiculo v : veiculos) {
                    System.out.println(v.getTipo() + " " + v.getPlaca() + " " + v.getTempoPermanencia() + " " + v.calculaEstadia());
                }
            } else {
                System.out.println("fail: comando invalido\n");
            }
        }
    }
}
```