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
        return this.capacity
    }

    fun getVolume(): Int {
        return this.volume
    }

    fun getTemperature(): Int {
        return this.temperature
    }

    fun addVolume(amount: Int): Boolean {
        if (amount <= 0) {
            return false
        }
        if (this.volume + amount > this.capacity) {
            return false
        }
        this.volume += amount
        return true
    }

    fun serve(amount: Int): Boolean {
        if (amount <= 0) {
            return false
        }
        if (amount > this.volume) {
            return false
        }
        this.volume -= amount
        return true
    }

    fun setTemperature(temperature: Int): Boolean {
        if (temperature < MIN_TEMPERATURE || temperature > MAX_TEMPERATURE) {
            return false
        }
        this.temperature = temperature
        return true
    }

    override fun toString(): String {
        return "capacity: ${this.capacity}, volume: ${this.volume}, temperature: ${this.temperature}"
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