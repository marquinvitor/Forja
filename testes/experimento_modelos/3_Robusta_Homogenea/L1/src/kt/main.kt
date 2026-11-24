const val INVALID_REFILL_MSG: String = "fail: invalid refill"
const val INVALID_SERVE_MSG: String = "fail: invalid serve"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class SmartFlask(capacity: Int = 0) {
    private var capacity: Int = 0
    private var volume: Int = 0
    private var temperature: Int = 0

    init {
        this.capacity = capacity
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

    fun refill(amount: Int, temp: Int): Boolean {
        if (amount <= 0 || temp <= 0 || this.volume + amount > this.capacity) {
            return false
        }
        this.volume += amount
        this.temperature = temp
        return true
    }

    fun serve(amount: Int): Boolean {
        if (amount <= 0 || amount > this.volume) {
            return false
        }
        this.volume -= amount
        if (this.volume == 0) {
            this.temperature = 0
        }
        return true
    }

    override fun toString(): String {
        return "flask: ${this.volume}/${this.capacity}ml, ${this.temperature}°C"
    }
}

fun main(): Unit {
    var flask: SmartFlask = SmartFlask(0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> flask = SmartFlask(parts[1].toInt())
            "show" -> println(flask)
            "refill" -> if (!flask.refill(parts[1].toInt(), parts[2].toInt())) {
                println(INVALID_REFILL_MSG)
            }
            "serve" -> if (!flask.serve(parts[1].toInt())) {
                println(INVALID_SERVE_MSG)
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}