const val SUCCESS_MSG: String = "success"
const val BIKE_ALREADY_EXISTS_MSG: String = "fail: bike already exists"
const val BIKE_NOT_FOUND_MSG: String = "fail: bike not found"
const val INVALID_KM_MSG: String = "fail: invalid km"
const val EMPTY_WORKSHOP_MSG: String = "fail: empty workshop"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

abstract class Bicicleta(codigo: String, quilometragem: Int) {
    private var codigo: String = ""
    private var quilometragem: Int = 0

    init {
        this.codigo = codigo
        if (quilometragem >= 0) {
            this.quilometragem = quilometragem
        } else {
            this.quilometragem = 0
        }
    }

    fun getCodigo(): String {
        return this.codigo
    }

    fun getQuilometragem(): Int {
        return this.quilometragem
    }

    fun setQuilometragem(km: Int): Boolean {
        if (km >= 0) {
            this.quilometragem = km
            return true
        }
        return false
    }

    abstract fun calcularRevisao(): Double

    abstract override fun toString(): String
}

class BicicletaUrbana(codigo: String, quilometragem: Int) : Bicicleta(codigo, quilometragem) {
    init {
    }

    override fun calcularRevisao(): Double {
        return 50.0 + (this.getQuilometragem() * 0.10)
    }

    override fun toString(): String {
        return "urbana: ${this.getCodigo()}, km: ${this.getQuilometragem()}, cost: ${this.calcularRevisao()}"
    }
}

class BicicletaEletrica(codigo: String, quilometragem: Int, potencia: Int) : Bicicleta(codigo, quilometragem) {
    private var potencia: Int = 0

    init {
        this.potencia = potencia
    }

    fun getPotencia(): Int {
        return this.potencia
    }

    override fun calcularRevisao(): Double {
        var custo: Double = 100.0 + (this.getQuilometragem() * 0.20)
        if (this.potencia > 250) {
            custo += 50.0
        }
        return custo
    }

    override fun toString(): String {
        return "eletrica: ${this.getCodigo()}, km: ${this.getQuilometragem()}, potencia: ${this.potencia}W, cost: ${this.calcularRevisao()}"
    }
}

class Oficina {
    private val bicicletas: MutableMap<String, Bicicleta> = mutableMapOf()

    fun adicionarBicicleta(bike: Bicicleta): Boolean {
        if (this.bicicletas.containsKey(bike.getCodigo())) {
            return false
        }
        this.bicicletas[bike.getCodigo()] = bike
        return true
    }

    fun buscarBicicleta(codigo: String): Bicicleta? {
        return this.bicicletas[codigo]
    }

    fun obterTodas(): List<Bicicleta> {
        val chavesOrdenadas: List<String> = this.bicicletas.keys.sorted()
        val resultado: MutableList<Bicicleta> = mutableListOf()
        for (chave: String in chavesOrdenadas) {
            val bike: Bicicleta? = this.bicicletas[chave]
            if (bike != null) {
                resultado.add(bike)
            }
        }
        return resultado
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