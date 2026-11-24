const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Book(id: String, title: String) {
    private var id: String = ""
    private var title: String = ""
    private var available: Boolean = true

    init {
        this.id = id
        this.title = title
        this.available = true
    }

    fun getId(): String {
        return this.id
    }

    fun getTitle(): String {
        return this.title
    }

    fun isAvailable(): Boolean {
        return this.available
    }

    fun borrow(): Unit {
        if (!this.available) {
            throw IllegalStateException("fail: livro indisponivel")
        }
        this.available = false
    }

    fun returnBook(): Unit {
        if (this.available) {
            throw IllegalStateException("fail: livro ja disponivel")
        }
        this.available = true
    }

    override fun toString(): String {
        val status: String = if (this.available) "disponivel" else "emprestado"
        return "${this.id}: ${this.title} ($status)"
    }
}

class Member(id: String, name: String, limit: Int) {
    private var id: String = ""
    private var name: String = ""
    private var limit: Int = 0
    private val borrowedBooks: MutableMap<String, Book> = linkedMapOf()

    init {
        if (limit <= 0) {
            throw IllegalArgumentException("fail: limite invalido")
        }
        this.id = id
        this.name = name
        this.limit = limit
    }

    fun getId(): String {
        return this.id
    }

    fun getName(): String {
        return this.name
    }

    fun getLimit(): Int {
        return this.limit
    }

    fun getBorrowedBooks(): List<Book> {
        return this.borrowedBooks.values.toList()
    }

    fun canBorrow(): Boolean {
        return this.borrowedBooks.size < this.limit
    }

    fun hasBook(bookId: String): Boolean {
        return this.borrowedBooks.containsKey(bookId)
    }

    fun addBook(book: Book): Unit {
        if (!this.canBorrow()) {
            throw IllegalStateException("fail: limite de emprestimos atingido")
        }
        this.borrowedBooks[book.getId()] = book
    }

    fun removeBook(bookId: String): Book {
        if (!this.hasBook(bookId)) {
            throw IllegalStateException("fail: socio nao possui este livro")
        }
        return this.borrowedBooks.remove(bookId)!!
    }

    override fun toString(): String {
        val ids: String = this.borrowedBooks.keys.joinToString(", ")
        return "${this.id}: ${this.name} [${this.borrowedBooks.size}/${this.limit}] -> [$ids]"
    }
}

class Library {
    private val books: MutableMap<String, Book> = linkedMapOf()
    private val members: MutableMap<String, Member> = linkedMapOf()

    fun addBook(book: Book): Unit {
        if (this.books.containsKey(book.getId())) {
            throw IllegalArgumentException("fail: livro ja cadastrado")
        }
        this.books[book.getId()] = book
    }

    fun addMember(member: Member): Unit {
        if (this.members.containsKey(member.getId())) {
            throw IllegalArgumentException("fail: socio ja cadastrado")
        }
        this.members[member.getId()] = member
    }

    fun getBook(id: String): Book {
        return this.books[id] ?: throw IllegalArgumentException("fail: livro nao encontrado")
    }

    fun getMember(id: String): Member {
        return this.members[id] ?: throw IllegalArgumentException("fail: socio nao encontrado")
    }

    fun borrowBook(memberId: String, bookId: String): Unit {
        val member: Member = this.getMember(memberId)
        val book: Book = this.getBook(bookId)

        if (!book.isAvailable()) {
            throw IllegalStateException("fail: livro indisponivel")
        }
        if (!member.canBorrow()) {
            throw IllegalStateException("fail: limite de emprestimos atingido")
        }

        book.borrow()
        member.addBook(book)
    }

    fun returnBook(memberId: String, bookId: String): Unit {
        val member: Member = this.getMember(memberId)
        val book: Book = this.getBook(bookId)

        member.removeBook(bookId)
        book.returnBook()
    }

    fun getBooks(): List<Book> {
        return this.books.values.toList()
    }

    fun getMembers(): List<Member> {
        return this.members.values.toList()
    }
}

fun main(): Unit {
    val library: Library = Library()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "addBook" -> try {
                library.addBook(Book(parts[1], parts[2]))
            } catch (e: Exception) {
                println(e.message)
            }
            "addMember" -> try {
                library.addMember(Member(parts[1], parts[2], parts[3].toInt()))
            } catch (e: Exception) {
                println(e.message)
            }
            "books" -> for (book: Book in library.getBooks()) {
                println(book)
            }
            "members" -> for (member: Member in library.getMembers()) {
                println(member)
            }
            "borrow" -> try {
                library.borrowBook(parts[1], parts[2])
            } catch (e: Exception) {
                println(e.message)
            }
            "return" -> try {
                library.returnBook(parts[1], parts[2])
            } catch (e: Exception) {
                println(e.message)
            }
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}