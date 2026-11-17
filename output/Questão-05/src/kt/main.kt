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
        return name
    }

    fun getPrice(): Double {
        return price
    }

    fun getQuantity(): Int {
        return quantity
    }

    fun setQuantity(quantity: Int): Boolean {
        if (quantity > 0) {
            this.quantity = quantity
            return true
        }
        return false
    }

    fun getTotal(): Double {
        return price * quantity
    }

    override fun toString(): String {
        return "$name: $price x $quantity"
    }
}

class Cart(private val maxCapacity: Int = 0) {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        if (items.size < maxCapacity) {
            items.add(item)
            return true
        }
        return false
    }

    fun removeItem(index: Int): Boolean {
        if (index in 0 until items.size) {
            items.removeAt(index)
            return true
        }
        return false
    }

    fun getTotalValue(): Double {
        return items.sumOf { it.getTotal() }
    }

    fun getItems(): List<Item> {
        return items.toList()
    }

    override fun toString(): String {
        val itemsStr: String = items.joinToString(", ") { it.toString() }
        return "cart: [$itemsStr], total: ${getTotalValue()}"
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