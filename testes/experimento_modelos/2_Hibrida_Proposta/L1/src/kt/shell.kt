const val OVERFLOW_MSG: String = "fail: overflow"
const val NOT_ENOUGH_WATER_MSG: String = "fail: not enough water"
const val INVALID_TEMPERATURE_MSG: String = "fail: invalid temperature"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class ThermoBottle(private val capacity: Int, private var temperature: Int) {
    companion object {
        const val MIN_TEMPERATURE: Int = 0
        const val MAX_TEMPERATURE: Int = 100
    }

    private var volume: Int = 0

    fun getCapacity(): Int {
        TODO("retorne a capacidade maxima da garrafa")
    }

    fun getVolume(): Int {
        TODO("retorne o volume atual de liquido")
    }

    fun getTemperature(): Int {
        TODO("retorne a temperatura atual")
    }

    fun addVolume(amount: Int): Boolean {
        TODO("adicione o volume especificado caso amount seja positivo e nao cause transbordamento")
    }

    fun serve(amount: Int): Boolean {
        TODO("retire o volume especificado caso amount seja positivo e nao exceda o volume atual")
    }

    fun setTemperature(temperature: Int): Boolean {
        TODO("atualize a temperatura caso esteja na faixa operacional segura de 0 a 100")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato: capacity: {capacity}, volume: {volume}, temperature: {temperature}")
    }
}

fun main(): Unit {
    var bottle: ThermoBottle = ThermoBottle(0, 0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> bottle = ThermoBottle(parts[1].toInt(), parts[2].toInt())
            "show" -> println(bottle)
            "add" -> if (!bottle.addVolume(parts[1].toInt())) {
                println(OVERFLOW_MSG)
            }
            "serve" -> if (!bottle.serve(parts[1].toInt())) {
                println(NOT_ENOUGH_WATER_MSG)
            }
            "temp" -> if (!bottle.setTemperature(parts[1].toInt())) {
                println(INVALID_TEMPERATURE_MSG)
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}