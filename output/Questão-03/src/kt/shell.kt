const val CART_FULL_MSG: String = "fail: cart is full"
const val INVALID_ITEM_MSG: String = "fail: invalid item"
const val INVALID_INDEX_MSG: String = "fail: invalid index"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Item(
    private val name: String = "",
    private val price: Double = 0.0,
    private var quantity: Int = 0
) {
    fun getName(): String {
        TODO("retorne o nome do item")
    }

    fun getPrice(): Double {
        TODO("retorne o preco do item")
    }

    fun getQuantity(): Int {
        TODO("retorne a quantidade do item")
    }

    fun setQuantity(quantity: Int): Boolean {
        TODO("valide e atualize a quantidade se for maior que zero")
    }

    fun getTotal(): Double {
        TODO("calcule e retorne o subtotal do item (preco * quantidade)")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato 'name: price x quantity'")
    }
}

class Cart(private val maxCapacity: Int = 0) {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        TODO("adicione o item caso a capacidade maxima nao tenha sido atingida")
    }

    fun removeItem(index: Int): Boolean {
        TODO("remova o item pelo indice se valido e retorne true, senao false")
    }

    fun getTotalValue(): Double {
        TODO("calcule e retorne a soma dos subtotais de todos os itens")
    }

    fun getItems(): List<Item> {
        TODO("retorne uma visao somente leitura da lista de itens")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual no formato 'cart: [...], total: valor'")
    }
}

fun main(): Unit {
    var cart: Cart = Cart(0)

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "init" -> cart = Cart(parts[1].toInt())
            "show" -> println(cart)
            "add" -> {
                val name: String = parts[1]
                val price: Double = parts[2].toDouble()
                val quantity: Int = parts[3].toInt()
                if (price <= 0.0 || quantity <= 0) {
                    println(INVALID_ITEM_MSG)
                } else {
                    val item: Item = Item(name, price, quantity)
                    if (!cart.addItem(item)) {
                        println(CART_FULL_MSG)
                    }
                }
            }
            "remove" -> {
                val index: Int = parts[1].toInt()
                if (!cart.removeItem(index)) {
                    println(INVALID_INDEX_MSG)
                }
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}