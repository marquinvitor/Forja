const val EXISTING_ITEM_MSG: String = "fail: existing item"
const val INVALID_QUANTITY_MSG: String = "fail: invalid quantity"
const val ITEM_NOT_FOUND_MSG: String = "fail: item not found"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Item(private val name: String, private val price: Double, private var quantity: Int) {
    companion object {
        const val MIN_QUANTITY: Int = 1
        const val MAX_QUANTITY: Int = 10
    }

    init {
        // TODO: inicialize os atributos
    }

    fun getName(): String {
        TODO("retorne o nome do item")
    }

    fun getPrice(): Double {
        TODO("retorne o preço do item")
    }

    fun getQuantity(): Int {
        TODO("retorne a quantidade do item")
    }

    fun setQuantity(qty: Int): Boolean {
        TODO("valide e atualize a quantidade respeitando os limites")
    }

    override fun toString(): String {
        TODO("retorne a representação textual do item no formato nome: quantidade x preço")
    }
}

class Cart {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        TODO("adicione o item se não existir duplicado e se for válido")
    }

    fun removeItem(name: String): Boolean {
        TODO("remova o item pelo nome e retorne verdadeiro se encontrado")
    }

    fun getItems(): List<Item> {
        TODO("retorne a lista de itens")
    }

    fun getTotal(): Double {
        TODO("calcule e retorne o valor total do carrinho")
    }
}

fun main(): Unit {
    var currentCart: Cart = Cart()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        if (parts.isEmpty() || parts[0].isEmpty()) {
            continue
        }

        when (parts[0]) {
            "end" -> break
            "init" -> currentCart = Cart()
            "add" -> {
                val name: String = parts[1]
                val price: Double = parts[2].toDouble()
                val quantity: Int = parts[3].toInt()
                
                if (quantity < Item.MIN_QUANTITY || quantity > Item.MAX_QUANTITY) {
                    println(INVALID_QUANTITY_MSG)
                } else {
                    val newItem: Item = Item(name, price, quantity)
                    if (!currentCart.addItem(newItem)) {
                        println(EXISTING_ITEM_MSG)
                    }
                }
            }
            "remove" -> {
                val name: String = parts[1]
                if (!currentCart.removeItem(name)) {
                    println(ITEM_NOT_FOUND_MSG)
                }
            }
            "show" -> {
                for (item: Item in currentCart.getItems()) {
                    println(item)
                }
                println("total: " + "%.2f".format(currentCart.getTotal()))
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}