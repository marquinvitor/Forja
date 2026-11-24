const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Book(private val id: String, private val title: String) {
    private var isAvailable: Boolean = true

    fun getId(): String {
        TODO("retorne o id do livro")
    }

    fun getTitle(): String {
        TODO("retorne o título do livro")
    }

    fun isAvailable(): Boolean {
        TODO("retorne a disponibilidade do livro")
    }

    fun setAvailable(status: Boolean): Unit {
        TODO("atualize a disponibilidade do livro")
    }

    override fun toString(): String {
        TODO("retorne a representação textual do livro no formato esperado")
    }
}

class Member(private val id: String, private val maxLoans: Int) {
    private val borrowedBooks: MutableMap<String, Book> = mutableMapOf()

    fun getId(): String {
        TODO("retorne o id do sócio")
    }

    fun getMaxLoans(): Int {
        TODO("retorne o limite máximo de empréstimos")
    }

    fun getBorrowedCount(): Int {
        TODO("retorne a quantidade de livros atualmente emprestados")
    }

    fun borrowBook(book: Book): Unit {
        TODO("adicione o livro aos empréstimos se o limite não for excedido")
    }

    fun returnBook(book: Book): Unit {
        TODO("remova o livro dos empréstimos se ele estiver com o sócio")
    }

    override fun toString(): String {
        TODO("retorne a representação textual do sócio no formato esperado")
    }
}

class Library {
    private val books: MutableMap<String, Book> = mutableMapOf()
    private val members: MutableMap<String, Member> = mutableMapOf()

    fun addBook(book: Book): Unit {
        TODO("adicione o livro ao mapa se não existir, senão lance exceção")
    }

    fun addMember(member: Member): Unit {
        TODO("adicione o sócio ao mapa se não existir, senão lance exceção")
    }

    fun borrowBook(memberId: String, bookId: String): Unit {
        TODO("realize o empréstimo validando a existência de sócio/livro e regras de negócio")
    }

    fun returnBook(memberId: String, bookId: String): Unit {
        TODO("realize a devolução validando a existência de sócio/livro")
    }

    fun show(): String {
        TODO("retorne a representação textual completa da biblioteca")
    }
}

fun main(): Unit {
    var library: Library = Library()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        if (parts.isEmpty() || parts[0].isEmpty()) continue

        try {
            when (parts[0]) {
                "end" -> break
                "init" -> library = Library()
                "addBook" -> library.addBook(Book(parts[1], parts[2]))
                "addMember" -> library.addMember(Member(parts[1], parts[2].toInt()))
                "show" -> print(library.show())
                "borrow" -> library.borrowBook(parts[1], parts[2])
                "return" -> library.returnBook(parts[1], parts[2])
                else -> println(INVALID_COMMAND_MSG)
            }
        } catch (e: Exception) {
            println(e.message)
        }
    }
}