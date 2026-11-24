const val INVALID_QUANTITY_MSG: String = "fail: invalid quantity"
const val ITEM_ALREADY_EXISTS_MSG: String = "fail: item already exists"
const val ITEM_NOT_FOUND_MSG: String = "fail: item not found"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Item(
    private val name: String = "",
    private val price: Double = 0.0,
    private var quantity: Int = 0
) {
    companion object {
        const val MIN_QUANTITY: Int = 1
        const val MAX_QUANTITY: Int = 10
    }

    fun getName(): String {
        TODO("retorne o nome do item")
    }

    fun getPrice(): Double {
        TODO("retorne o preco unitario do item")
    }

    fun getQuantity(): Int {
        TODO("retorne a quantidade do item")
    }

    fun setQuantity(quantity: Int): Boolean {
        TODO("atualize a quantidade se estiver entre MIN_QUANTITY e MAX_QUANTITY e retorne true, senao retorne false")
    }

    fun getTotal(): Double {
        TODO("calcule e retorne o subtotal multiplicando o preco pela quantidade")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do item no formato 'name: quantity: price'")
    }
}

class Cart {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        TODO("adicione o item se ele ainda nao estiver presente na lista ignorando maiusculas/minusculas e retorne true, senao retorne false")
    }

    fun getItem(name: String): Item? {
        TODO("busque e retorne o item pelo nome ignorando maiusculas/minusculas, ou null caso nao exista")
    }

    fun removeItem(name: String): Boolean {
        TODO("remova o item pelo nome e retorne true se removido, senao retorne false")
    }

    fun getItems(): List<Item> {
        TODO("retorne a lista de itens do carrinho")
    }

    fun getTotal(): Double {
        TODO("calcule e retorne a soma dos subtotais de todos os itens do carrinho")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do carrinho exibindo os itens e a linha final com o total")
    }
}

fun main(): Unit {
    val cart: Cart = Cart()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "add" -> {
                val item: Item = Item(parts[1], parts[2].toDouble())
                if (!item.setQuantity(parts[3].toInt())) {
                    println(INVALID_QUANTITY_MSG)
                } else if (!cart.addItem(item)) {
                    println(ITEM_ALREADY_EXISTS_MSG)
                }
            }
            "qty" -> {
                val item: Item? = cart.getItem(parts[1])
                if (item == null) {
                    println(ITEM_NOT_FOUND_MSG)
                } else if (!item.setQuantity(parts[2].toInt())) {
                    println(INVALID_QUANTITY_MSG)
                }
            }
            "remove" -> if (!cart.removeItem(parts[1])) {
                println(ITEM_NOT_FOUND_MSG)
            }
            "show" -> println(cart)
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}