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
        return this.name
    }

    fun getAge(): Int {
        return this.age
    }

    fun canRide(): Boolean {
        return this.age >= MIN_AGE
    }

    override fun toString(): String {
        return "name:${this.name}, age:${this.age}"
    }
}

class Scooter(private val id: String) {
    private var batteryMinutes: Int = 0
    private var user: User? = null

    fun getId(): String {
        return this.id
    }

    fun getBattery(): Int {
        return this.batteryMinutes
    }

    fun getUser(): User? {
        return this.user
    }

    fun charge(minutes: Int): Unit {
        if (minutes > 0) {
            this.batteryMinutes += minutes
        }
    }

    fun enter(user: User): EnterResult {
        if (this.user != null) {
            return EnterResult.BUSY
        }
        if (!user.canRide()) {
            return EnterResult.TOO_YOUNG
        }
        this.user = user
        return EnterResult.SUCCESS
    }

    fun leave(): LeaveResult {
        if (this.user == null) {
            return LeaveResult.NO_USER
        }
        this.user = null
        return LeaveResult.SUCCESS
    }

    fun drive(minutes: Int): DriveResult {
        if (this.user == null) {
            return DriveResult.NO_USER
        }
        if (this.batteryMinutes < minutes) {
            return DriveResult.BATTERY_DEPLETED
        }
        this.batteryMinutes -= minutes
        return DriveResult.SUCCESS
    }

    override fun toString(): String {
        val userInfo: String = if (this.user != null) "(${this.user})" else "(empty)"
        return "id:${this.id}, battery:${this.batteryMinutes}, user:${userInfo}"
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