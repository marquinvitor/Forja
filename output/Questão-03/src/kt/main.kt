const val CAPACITY_MUST_BE_POSITIVE_MSG: String = "fail: capacity must be positive"
const val NEGATIVE_VALUE_MSG: String = "fail: negative value"
const val OVERFLOW_MSG: String = "fail: overflow"
const val NOT_ENOUGH_WATER_MSG: String = "fail: not enough water"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class ThermalBottle(capacity: Int = 0) {
    private var capacity: Int = 0
    private var volume: Int = 0
    private var temperature: Int = 0

    init {
        if (capacity > 0) {
            this.capacity = capacity
        }
        this.volume = 0
        this.temperature = 0
    }

    fun getCapacity(): Int {
        return this.capacity
    }

    fun getVolume(): Int {
        return this.volume
    }

    fun getTemperature(): Int {
        return this.temperature
    }

    fun fill(volume: Int, temperature: Int): Boolean {
        if (volume < 0 || temperature < 0) {
            return false
        }
        if (this.volume + volume > this.capacity) {
            return false
        }
        this.volume += volume
        this.temperature = temperature
        return true
    }

    fun serve(volume: Int): Boolean {
        if (volume < 0) {
            return false
        }
        if (volume > this.volume) {
            return false
        }
        this.volume -= volume
        if (this.volume == 0) {
            this.temperature = 0
        }
        return true
    }

    override fun toString(): String {
        return "capacity: ${this.capacity}, volume: ${this.volume}, temperature: ${this.temperature}"
    }
}

fun main(): Unit {
    var bottle: ThermalBottle = ThermalBottle(0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> {
                val capacity: Int = parts[1].toInt()
                if (capacity <= 0) {
                    println(CAPACITY_MUST_BE_POSITIVE_MSG)
                } else {
                    bottle = ThermalBottle(capacity)
                }
            }
            "show" -> println(bottle)
            "fill" -> {
                val volume: Int = parts[1].toInt()
                val temperature: Int = parts[2].toInt()
                if (volume < 0 || temperature < 0) {
                    println(NEGATIVE_VALUE_MSG)
                } else if (!bottle.fill(volume, temperature)) {
                    println(OVERFLOW_MSG)
                }
            }
            "serve" -> {
                val volume: Int = parts[1].toInt()
                if (volume < 0) {
                    println(NEGATIVE_VALUE_MSG)
                } else if (!bottle.serve(volume)) {
                    println(NOT_ENOUGH_WATER_MSG)
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}