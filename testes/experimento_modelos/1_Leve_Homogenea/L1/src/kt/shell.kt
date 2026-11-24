const val INVALID_CAPACITY_MSG: String = "fail: invalid capacity"
const val INVALID_VOLUME_MSG: String = "fail: invalid volume"
const val OVERFLOW_MSG: String = "fail: overflow"
const val EMPTY_BOTTLE_MSG: String = "fail: empty bottle"
const val INVALID_TEMPERATURE_MSG: String = "fail: invalid temperature"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class ThermalBottle(private val capacity: Int) {
    private var volume: Int = 0
    private var temperature: Int = 20

    init {
        // TODO: inicialize os atributos e valide a capacidade
    }

    fun getCapacity(): Int {
        TODO("retorne a capacidade")
    }

    fun getVolume(): Int {
        TODO("retorne o volume atual")
    }

    fun getTemperature(): Int {
        TODO("retorne a temperatura atual")
    }

    fun addWater(amount: Int): Boolean {
        TODO("adicione água respeitando capacidade e valores não negativos")
    }

    fun serveWater(amount: Int): Boolean {
        TODO("sirva água respeitando o volume atual e valores não negativos")
    }

    fun setTemperature(temp: Int): Boolean {
        TODO("altere a temperatura mantendo dentro dos limites operacionais")
    }

    override fun toString(): String {
        TODO("retorne a representação textual no formato exigido")
    }
}

fun main(): Unit {
    var currentBottle: ThermalBottle = ThermalBottle(0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> {
                val cap: Int = parts[1].toInt()
                if (cap <= 0) {
                    println(INVALID_CAPACITY_MSG)
                } else {
                    currentBottle = ThermalBottle(cap)
                }
            }
            "show" -> println(currentBottle)
            "add" -> {
                val amount: Int = parts[1].toInt()
                if (amount < 0) {
                    println(INVALID_VOLUME_MSG)
                } else if (!currentBottle.addWater(amount)) {
                    println(OVERFLOW_MSG)
                }
            }
            "serve" -> {
                val amount: Int = parts[1].toInt()
                if (amount < 0) {
                    println(INVALID_VOLUME_MSG)
                } else if (!currentBottle.serveWater(amount)) {
                    println(EMPTY_BOTTLE_MSG)
                }
            }
            "temp" -> {
                val temp: Int = parts[1].toInt()
                if (!currentBottle.setTemperature(temp)) {
                    println(INVALID_TEMPERATURE_MSG)
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}