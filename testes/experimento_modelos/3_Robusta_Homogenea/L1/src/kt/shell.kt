const val INVALID_REFILL_MSG: String = "fail: invalid refill"
const val INVALID_SERVE_MSG: String = "fail: invalid serve"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class SmartFlask(capacity: Int = 0) {
    private var capacity: Int = 0
    private var volume: Int = 0
    private var temperature: Int = 0

    init {
        // TODO: inicialize os atributos
    }

    fun getCapacity(): Int {
        TODO("retorne a capacidade maxima da garrafa")
    }

    fun getVolume(): Int {
        TODO("retorne o volume atual de liquido")
    }

    fun getTemperature(): Int {
        TODO("retorne a temperatura atual do liquido")
    }

    fun refill(amount: Int, temp: Int): Boolean {
        TODO("valide e execute o abastecimento, retornando true em sucesso ou false em falha")
    }

    fun serve(amount: Int): Boolean {
        TODO("valide e execute a retirada de liquido, retornando true em sucesso ou false em falha")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato flask: <volume>/<capacity>ml, <temp>°C")
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