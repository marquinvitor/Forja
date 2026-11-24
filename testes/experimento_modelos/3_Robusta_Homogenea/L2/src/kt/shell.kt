import java.util.Locale

const val INVALID_QUANTITY_MSG: String = "fail: invalid quantity"
const val CART_FULL_MSG: String = "fail: cart is full"
const val INVALID_INDEX_MSG: String = "fail: invalid index"
const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Item(private val name: String, private val unitPrice: Double) {
    companion object {
        const val MIN_QUANTITY: Int = 1
        const val MAX_QUANTITY: Int = 20
    }

    private var quantity: Int = 1

    fun getName(): String {
        TODO("retorne o nome do produto")
    }

    fun getUnitPrice(): Double {
        TODO("retorne o preco unitario do produto")
    }

    fun getQuantity(): Int {
        TODO("retorne a quantidade atual do produto")
    }

    fun setQuantity(quantity: Int): Boolean {
        TODO("valide a invariante de quantidade (entre 1 e 20) e atualize se for valida")
    }

    fun getTotal(): Double {
        TODO("calcule e retorne o subtotal do item multiplicando quantidade por preco unitario")
    }
}

class Cart(private val maxItems: Int) {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        TODO("adicione o item ao final da lista se nao exceder maxItems")
    }

    fun removeItem(index: Int): Boolean {
        TODO("remova o item pelo indice caso seja valido")
    }

    fun getItem(index: Int): Item? {
        TODO("retorne o item na posicao indicada ou null se o indice for invalido")
    }

    fun getItems(): List<Item> {
        TODO("retorne a lista de itens")
    }

    fun getTotal(): Double {
        TODO("calcule e retorne a soma dos subtotais de todos os itens do carrinho")
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
            "add" -> {
                val item: Item = Item(parts[1], parts[2].toDouble())
                if (!item.setQuantity(parts[3].toInt())) {
                    println(INVALID_QUANTITY_MSG)
                } else if (!cart.addItem(item)) {
                    println(CART_FULL_MSG)
                }
            }
            "set_qty" -> {
                val item: Item? = cart.getItem(parts[1].toInt())
                if (item == null) {
                    println(INVALID_INDEX_MSG)
                } else if (!item.setQuantity(parts[2].toInt())) {
                    println(INVALID_QUANTITY_MSG)
                }
            }
            "remove" -> {
                if (!cart.removeItem(parts[1].toInt())) {
                    println(INVALID_INDEX_MSG)
                }
            }
            "show" -> {
                val items: List<Item> = cart.getItems()
                for (i: Int in items.indices) {
                    val item: Item = items[i]
                    val name: String = item.getName()
                    val qty: Int = item.getQuantity()
                    val unitPrice: String = String.format(Locale.US, "%.2f", item.getUnitPrice())
                    val itemTotal: String = String.format(Locale.US, "%.2f", item.getTotal())
                    println("[$i] $name: $qty x $unitPrice = $itemTotal")
                }
                val cartTotal: String = String.format(Locale.US, "%.2f", cart.getTotal())
                println("total: $cartTotal")
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}