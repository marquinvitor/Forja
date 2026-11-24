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
        return this.name
    }

    fun getUnitPrice(): Double {
        return this.unitPrice
    }

    fun getQuantity(): Int {
        return this.quantity
    }

    fun setQuantity(quantity: Int): Boolean {
        if (quantity in MIN_QUANTITY..MAX_QUANTITY) {
            this.quantity = quantity
            return true
        }
        return false
    }

    fun getTotal(): Double {
        return this.unitPrice * this.quantity
    }
}

class Cart(private val maxItems: Int) {
    private val items: MutableList<Item> = mutableListOf()

    fun addItem(item: Item): Boolean {
        if (this.items.size < this.maxItems) {
            this.items.add(item)
            return true
        }
        return false
    }

    fun removeItem(index: Int): Boolean {
        if (index in 0 until this.items.size) {
            this.items.removeAt(index)
            return true
        }
        return false
    }

    fun getItem(index: Int): Item? {
        if (index in 0 until this.items.size) {
            return this.items[index]
        }
        return null
    }

    fun getItems(): List<Item> {
        return this.items
    }

    fun getTotal(): Double {
        var total: Double = 0.0
        for (item: Item in this.items) {
            total += item.getTotal()
        }
        return total
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