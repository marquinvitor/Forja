const val INVALID_COMMAND_MSG: String = "fail: invalid command"
const val INVALID_INDEX_MSG: String = "fail: invalid index"
const val BAY_OCCUPIED_MSG: String = "fail: bay is already occupied"
const val VEHICLE_ALREADY_PARKED_MSG: String = "fail: vehicle already parked"
const val BAY_EMPTY_MSG: String = "fail: bay is empty"

class Vehicle(private val plate: String = "") {
    fun getPlate(): String {
        TODO("retorne a placa do veículo")
    }

    override fun toString(): String {
        TODO("retorne a representação textual do veículo no formato [<plate>]")
    }
}

class ParkingLot(private val capacity: Int = 0) {
    private var bays: Array<Vehicle?> = arrayOfNulls<Vehicle>(0)

    init {
        // TODO: inicialize os atributos
    }

    fun getCapacity(): Int {
        TODO("retorne a capacidade total de vagas do estacionamento")
    }

    fun getVehicle(index: Int): Vehicle? {
        TODO("retorne o veículo na vaga index ou null se vazia/índice inválido")
    }

    fun findVehicle(plate: String): Int {
        TODO("retorne o índice da vaga onde o veículo está ou -1 se não estiver presente")
    }

    fun park(index: Int, vehicle: Vehicle): Boolean {
        TODO("valide o índice (INVALID_INDEX_MSG), se a vaga está ocupada (BAY_OCCUPIED_MSG) e se o veículo já está no pátio (VEHICLE_ALREADY_PARKED_MSG); estacione e retorne true")
    }

    fun leave(index: Int): Vehicle? {
        TODO("valide o índice (INVALID_INDEX_MSG) e se a vaga está vazia (BAY_EMPTY_MSG); libere a vaga e retorne o veículo removido")
    }

    override fun toString(): String {
        TODO("retorne a representação textual de todas as vagas, uma por linha (ex: '0: empty' ou '1: [CarA]')")
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