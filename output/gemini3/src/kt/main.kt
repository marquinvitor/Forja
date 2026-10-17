const val INVALID_COMMAND_MSG: String = "fail: invalid command"
const val INVALID_POSITION_MSG: String = "fail: invalid position"
const val DUPLICATE_BAGGAGE_MSG: String = "fail: duplicate baggage"
const val POSITION_OCCUPIED_MSG: String = "fail: position occupied"
const val EMPTY_POSITION_MSG: String = "fail: empty position"

enum class AddResult {
    SUCCESS,
    INVALID_POSITION,
    ALREADY_EXISTS,
    OCCUPIED
}

class Bagagem(private val codigo: String = "") {
    fun getCodigo(): String {
        return this.codigo
    }

    override fun toString(): String {
        return this.codigo
    }
}

class Esteira {
    companion object {
        const val CAPACIDADE: Int = 6
    }

    private var bagagens: Array<Bagagem?> = arrayOfNulls<Bagagem>(CAPACIDADE)

    fun posicaoValida(posicao: Int): Boolean {
        return posicao in 0 until CAPACIDADE
    }

    fun adicionar(bagagem: Bagagem, posicao: Int): AddResult {
        if (!posicaoValida(posicao)) {
            return AddResult.INVALID_POSITION
        }
        for (i: Int in 0 until CAPACIDADE) {
            val atual: Bagagem? = this.bagagens[i]
            if (atual != null && atual.getCodigo() == bagagem.getCodigo()) {
                return AddResult.ALREADY_EXISTS
            }
        }
        if (this.bagagens[posicao] != null) {
            return AddResult.OCCUPIED
        }
        this.bagagens[posicao] = bagagem
        return AddResult.SUCCESS
    }

    fun remover(posicao: Int): Bagagem? {
        if (!posicaoValida(posicao)) {
            return null
        }
        val bagagemRemovida: Bagagem? = this.bagagens[posicao]
        if (bagagemRemovida != null) {
            this.bagagens[posicao] = null
        }
        return bagagemRemovida
    }

    fun consultar(): Array<Bagagem?> {
        val copia: Array<Bagagem?> = arrayOfNulls<Bagagem>(CAPACIDADE)
        for (i: Int in 0 until CAPACIDADE) {
            copia[i] = this.bagagens[i]
        }
        return copia
    }

    override fun toString(): String {
        val sb: StringBuilder = StringBuilder()
        sb.append("[")
        for (i: Int in 0 until CAPACIDADE) {
            val bagagem: Bagagem? = this.bagagens[i]
            if (bagagem == null) {
                sb.append("empty")
            } else {
                sb.append(bagagem.toString())
            }
            if (i < CAPACIDADE - 1) {
                sb.append(", ")
            }
        }
        sb.append("]")
        return sb.toString()
    }
}

fun main(): Unit {
    val esteira: Esteira = Esteira()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "show" -> println(esteira)
            "add" -> when (esteira.adicionar(Bagagem(parts[1]), parts[2].toInt())) {
                AddResult.INVALID_POSITION -> println(INVALID_POSITION_MSG)
                AddResult.ALREADY_EXISTS -> println(DUPLICATE_BAGGAGE_MSG)
                AddResult.OCCUPIED -> println(POSITION_OCCUPIED_MSG)
                AddResult.SUCCESS -> {}
            }
            "remove" -> {
                val posicao: Int = parts[1].toInt()
                if (!esteira.posicaoValida(posicao)) {
                    println(INVALID_POSITION_MSG)
                } else if (esteira.remover(posicao) == null) {
                    println(EMPTY_POSITION_MSG)
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}