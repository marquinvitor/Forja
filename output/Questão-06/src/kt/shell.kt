const val SUCCESS_MSG: String = "success"
const val BIKE_ALREADY_EXISTS_MSG: String = "fail: bike already exists"
const val BIKE_NOT_FOUND_MSG: String = "fail: bike not found"
const val INVALID_KM_MSG: String = "fail: invalid km"
const val EMPTY_WORKSHOP_MSG: String = "fail: empty workshop"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

abstract class Bicicleta(codigo: String, quilometragem: Int) {
    private var codigo: String = ""
    private var quilometragem: Int = 0

    fun getCodigo(): String {
        TODO("retorne o codigo da bicicleta")
    }

    init {
        TODO("inicialize codigo e quilometragem, definindo quilometragem como 0 caso o valor informado seja negativo")
    }

    fun getQuilometragem(): Int {
        TODO("retorne a quilometragem atual da bicicleta")
    }

    fun setQuilometragem(km: Int): Boolean {
        TODO("atualize a quilometragem se km >= 0 e retorne true; caso contrario retorne false")
    }

    abstract fun calcularRevisao(): Double

    abstract override fun toString(): String
}

class BicicletaUrbana(codigo: String, quilometragem: Int) : Bicicleta(codigo, quilometragem) {
    init {
    }

    override fun calcularRevisao(): Double {
        TODO("calcule e retorne o custo da revisao da bicicleta urbana: 50.0 + 0.10 por km")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato 'urbana: codigo, km: quilometragem, cost: revisao'")
    }
}

class BicicletaEletrica(codigo: String, quilometragem: Int, potencia: Int) : Bicicleta(codigo, quilometragem) {
    private var potencia: Int = 0

    init {
        TODO("inicialize a potencia da bicicleta eletrica")
    }

    fun getPotencia(): Int {
        TODO("retorne a potencia da bicicleta eletrica")
    }

    override fun calcularRevisao(): Double {
        TODO("calcule e retorne o custo da revisao da bicicleta eletrica: 100.0 + 0.20 por km, somando 50.0 se potencia > 250")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato 'eletrica: codigo, km: quilometragem, potencia: potenciaW, cost: revisao'")
    }
}

class Oficina {
    private val bicicletas: MutableMap<String, Bicicleta> = mutableMapOf()

    fun adicionarBicicleta(bike: Bicicleta): Boolean {
        TODO("adicione a bicicleta ao mapa se o codigo ainda nao existir e retorne true; caso contrario retorne false")
    }

    fun buscarBicicleta(codigo: String): Bicicleta? {
        TODO("busque e retorne a bicicleta pelo codigo informado, ou null se nao existir")
    }

    fun obterTodas(): List<Bicicleta> {
        TODO("retorne a lista de todas as bicicletas cadastradas ordenadas pelo codigo")
    }
}

fun main(): Unit {
    val oficina: Oficina = Oficina()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "add_urbana" -> {
                val bike: BicicletaUrbana = BicicletaUrbana(parts[1], parts[2].toInt())
                if (oficina.adicionarBicicleta(bike)) {
                    println(SUCCESS_MSG)
                } else {
                    println(BIKE_ALREADY_EXISTS_MSG)
                }
            }
            "add_eletrica" -> {
                val bike: BicicletaEletrica = BicicletaEletrica(parts[1], parts[2].toInt(), parts[3].toInt())
                if (oficina.adicionarBicicleta(bike)) {
                    println(SUCCESS_MSG)
                } else {
                    println(BIKE_ALREADY_EXISTS_MSG)
                }
            }
            "set_km" -> {
                val bike: Bicicleta? = oficina.buscarBicicleta(parts[1])
                if (bike == null) {
                    println(BIKE_NOT_FOUND_MSG)
                } else if (bike.setQuilometragem(parts[2].toInt())) {
                    println(SUCCESS_MSG)
                } else {
                    println(INVALID_KM_MSG)
                }
            }
            "show" -> {
                val bike: Bicicleta? = oficina.buscarBicicleta(parts[1])
                if (bike == null) {
                    println(BIKE_NOT_FOUND_MSG)
                } else {
                    println(bike)
                }
            }
            "show_all" -> {
                val bikes: List<Bicicleta> = oficina.obterTodas()
                if (bikes.isEmpty()) {
                    println(EMPTY_WORKSHOP_MSG)
                } else {
                    for (bike: Bicicleta in bikes) {
                        println(bike)
                    }
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}