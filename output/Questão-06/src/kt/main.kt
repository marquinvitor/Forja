const val INVALID_COMMAND_MSG: String = "fail: invalid command"
const val INVALID_INDEX_MSG: String = "fail: invalid index"
const val BAY_OCCUPIED_MSG: String = "fail: bay is already occupied"
const val VEHICLE_ALREADY_PARKED_MSG: String = "fail: vehicle already parked"
const val BAY_EMPTY_MSG: String = "fail: bay is empty"

class Vehicle(private val plate: String = "") {
    fun getPlate(): String {
        return this.plate
    }

    override fun toString(): String {
        return "[${this.plate}]"
    }
}

class ParkingLot(private val capacity: Int = 0) {
    private var bays: Array<Vehicle?> = arrayOfNulls<Vehicle>(capacity)

    init {
        this.bays = arrayOfNulls<Vehicle>(this.capacity)
    }

    fun getCapacity(): Int {
        return this.capacity
    }

    fun getVehicle(index: Int): Vehicle? {
        if (index < 0 || index >= this.capacity) {
            return null
        }
        return this.bays[index]
    }

    fun findVehicle(plate: String): Int {
        var i: Int = 0
        while (i < this.capacity) {
            val v: Vehicle? = this.bays[i]
            if (v != null && v.getPlate() == plate) {
                return i
            }
            i = i + 1
        }
        return -1
    }

    fun park(index: Int, vehicle: Vehicle): Boolean {
        if (index < 0 || index >= this.capacity) {
            throw IllegalArgumentException(INVALID_INDEX_MSG)
        }
        if (this.bays[index] != null) {
            throw IllegalStateException(BAY_OCCUPIED_MSG)
        }
        if (this.findVehicle(vehicle.getPlate()) != -1) {
            throw IllegalStateException(VEHICLE_ALREADY_PARKED_MSG)
        }
        this.bays[index] = vehicle
        return true
    }

    fun leave(index: Int): Vehicle? {
        if (index < 0 || index >= this.capacity) {
            throw IllegalArgumentException(INVALID_INDEX_MSG)
        }
        val v: Vehicle? = this.bays[index]
        if (v == null) {
            throw IllegalStateException(BAY_EMPTY_MSG)
        }
        this.bays[index] = null
        return v
    }

    override fun toString(): String {
        var result: String = ""
        var i: Int = 0
        while (i < this.capacity) {
            val v: Vehicle? = this.bays[i]
            val line: String = if (v == null) {
                "${i}: empty"
            } else {
                "${i}: ${v.toString()}"
            }
            if (i > 0) {
                result = result + "\n"
            }
            result = result + line
            i = i + 1
        }
        return result
    }
}

fun main(): Unit {
    var parkingLot: ParkingLot = ParkingLot(0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> parkingLot = ParkingLot(parts[1].toInt())
            "show" -> println(parkingLot)
            "park" -> {
                try {
                    parkingLot.park(parts[1].toInt(), Vehicle(parts[2]))
                } catch (e: Exception) {
                    println(e.message)
                }
            }
            "leave" -> {
                try {
                    parkingLot.leave(parts[1].toInt())
                } catch (e: Exception) {
                    println(e.message)
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}