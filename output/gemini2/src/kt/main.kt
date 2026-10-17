const val INVALID_COMMAND_MSG: String = "fail: invalid command"
const val FLIGHT_ALREADY_EXISTS_MSG: String = "fail: flight already exists"
const val SEAT_UNAVAILABLE_MSG: String = "fail: seat unavailable"
const val SEAT_EMPTY_OR_INVALID_MSG: String = "fail: seat empty or invalid"
const val NO_PILOT_MSG: String = "fail: flight cannot depart without pilot"

class Piloto(private val name: String, private val license: String) {
    fun getName(): String = name
    fun getLicense(): String = license

    override fun toString(): String = "$name ($license)"
}

class Assento(private val id: Int) {
    private var passenger: String? = null

    fun getId(): Int = id
    fun getPassenger(): String? = passenger

    fun setPassenger(name: String?): Unit {
        passenger = name
    }

    override fun toString(): String = "Seat $id: ${passenger ?: "empty"}"
}

class Voo(private val flightId: String, capacity: Int) {
    private val seats: MutableList<Assento> = mutableListOf()
    private var pilot: Piloto? = null
    private var isDeparted: Boolean = false

    init {
        for (i: Int in 0 until capacity) {
            seats.add(Assento(i))
        }
    }

    fun getFlightId(): String = flightId
    fun getPilot(): Piloto? = pilot
    fun isDeparted(): Boolean = isDeparted

    fun setPilot(pilot: Piloto?): Boolean {
        this.pilot = pilot
        return true
    }

    fun reserve(seatId: Int, passenger: String): Boolean {
        val seat: Assento? = seats.find { s: Assento -> s.getId() == seatId }
        if (seat == null || seat.getPassenger() != null) {
            return false
        }
        seat.setPassenger(passenger)
        return true
    }

    fun cancel(seatId: Int): Boolean {
        val seat: Assento? = seats.find { s: Assento -> s.getId() == seatId }
        if (seat == null || seat.getPassenger() == null) {
            return false
        }
        seat.setPassenger(null)
        return true
    }

    fun depart(): Boolean {
        if (pilot == null || isDeparted) {
            return false
        }
        isDeparted = true
        return true
    }

    override fun toString(): String {
        val pilotStr: String = if (pilot != null) pilot.toString() else "none"
        val statusStr: String = if (isDeparted) "departed" else "on-ground"
        val sb: StringBuilder = StringBuilder()
        sb.append("Flight: $flightId | Pilot: $pilotStr | Status: $statusStr")
        for (s: Assento in seats) {
            sb.append("\n- $s")
        }
        return sb.toString()
    }
}

fun main(): Unit {
    var flight: Voo = Voo("", 0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> {
                val flightId: String = parts[1]
                val capacity: Int = parts[2].toInt()
                if (flight.getFlightId().isNotEmpty()) { println(FLIGHT_ALREADY_EXISTS_MSG) } else { flight = Voo(flightId, capacity) }
            }
            "show" -> {
                println(flight)
            }
            "set_pilot" -> {
                val name: String = parts[1]
                val license: String = parts[2]
                flight.setPilot(Piloto(name, license))
            }
            "reserve" -> {
                val seatId: Int = parts[1].toInt()
                val passenger: String = parts[2]
                if (!flight.reserve(seatId, passenger)) { println(SEAT_UNAVAILABLE_MSG) }
            }
            "cancel" -> {
                val seatId: Int = parts[1].toInt()
                if (!flight.cancel(seatId)) { println(SEAT_EMPTY_OR_INVALID_MSG) }
            }
            "depart" -> {
                if (!flight.depart()) { println(NO_PILOT_MSG) }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}
