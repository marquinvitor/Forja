const val SCOOTER_BUSY_MSG: String = "fail: scooter is busy"
const val USER_TOO_YOUNG_MSG: String = "fail: user too young"
const val NO_USER_MSG: String = "fail: no user on scooter"
const val BATTERY_DEPLETED_MSG: String = "fail: battery depleted"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

enum class EnterResult {
    SUCCESS,
    BUSY,
    TOO_YOUNG
}

enum class LeaveResult {
    SUCCESS,
    NO_USER
}

enum class DriveResult {
    SUCCESS,
    NO_USER,
    BATTERY_DEPLETED
}

class User(private val name: String, private val age: Int) {
    companion object {
        const val MIN_AGE: Int = 18
    }

    fun getName(): String {
        TODO("retorne o nome do usuario")
    }

    fun getAge(): Int {
        TODO("retorne a idade do usuario")
    }

    fun canRide(): Boolean {
        TODO("retorne true se a idade for maior ou igual a MIN_AGE, ou false caso contrario")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato name:NOME, age:IDADE")
    }
}

class Scooter(private val id: String) {
    private var batteryMinutes: Int = 0
    private var user: User? = null

    fun getId(): String {
        TODO("retorne o identificador do patinete")
    }

    fun getBattery(): Int {
        TODO("retorne os minutos de bateria restantes")
    }

    fun getUser(): User? {
        TODO("retorne a referencia ao usuario embarcado ou null se vazio")
    }

    fun charge(minutes: Int): Unit {
        TODO("adicione os minutos positivos a carga de bateria")
    }

    fun enter(user: User): EnterResult {
        TODO("embarque o usuario checando se ja esta ocupado e delegando canRide() para validacao de idade")
    }

    fun leave(): LeaveResult {
        TODO("desembarque o usuario atual ou retorne NO_USER se ja estiver vazio")
    }

    fun drive(minutes: Int): DriveResult {
        TODO("realize a corrida consumindo minutos se houver usuario e bateria suficiente")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato id:ID, battery:BATTERY, user:(USER|empty)")
    }
}

fun main(): Unit {
    var scooter: Scooter = Scooter("")

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> scooter = Scooter(parts[1])
            "show" -> println(scooter)
            "charge" -> scooter.charge(parts[1].toInt())
            "enter" -> when (scooter.enter(User(parts[1], parts[2].toInt()))) {
                EnterResult.BUSY -> println(SCOOTER_BUSY_MSG)
                EnterResult.TOO_YOUNG -> println(USER_TOO_YOUNG_MSG)
                EnterResult.SUCCESS -> {}
            }
            "leave" -> when (scooter.leave()) {
                LeaveResult.NO_USER -> println(NO_USER_MSG)
                LeaveResult.SUCCESS -> {}
            }
            "drive" -> when (scooter.drive(parts[1].toInt())) {
                DriveResult.NO_USER -> println(NO_USER_MSG)
                DriveResult.BATTERY_DEPLETED -> println(BATTERY_DEPLETED_MSG)
                DriveResult.SUCCESS -> {}
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}