const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Livro(private val id: String = "", private val titulo: String = "") {
    private var disponivel: Boolean = true

    fun getId(): String {
        return this.id
    }

    fun getTitulo(): String {
        return this.titulo
    }

    fun isDisponivel(): Boolean {
        return this.disponivel
    }

    fun emprestar(): Unit {
        if (!this.disponivel) {
            throw IllegalStateException("book not available")
        }
        this.disponivel = false
    }

    fun devolver(): Unit {
        if (this.disponivel) {
            throw IllegalStateException("book not loaned")
        }
        this.disponivel = true
    }

    override fun toString(): String {
        return "livro: ${this.id}, ${this.titulo}, disponivel: ${this.disponivel}"
    }
}

class Socio(private val id: String = "", private val nome: String = "", private var limite: Int = 0) {
    private val livrosEmprestados: MutableList<Livro> = mutableListOf()

    init {
        if (this.limite <= 0) {
            throw IllegalArgumentException("invalid limit")
        }
    }

    fun getId(): String {
        return this.id
    }

    fun getNome(): String {
        return this.nome
    }

    fun getLimite(): Int {
        return this.limite
    }

    fun adicionarLivro(livro: Livro): Unit {
        if (this.livrosEmprestados.size >= this.limite) {
            throw IllegalStateException("socio reached loan limit")
        }
        this.livrosEmprestados.add(livro)
    }

    fun removerLivro(livroId: String): Boolean {
        val iterator: MutableIterator<Livro> = this.livrosEmprestados.iterator()
        while (iterator.hasNext()) {
            val livro: Livro = iterator.next()
            if (livro.getId() == livroId) {
                iterator.remove()
                return true
            }
        }
        return false
    }

    fun qtdEmprestados(): Int {
        return this.livrosEmprestados.size
    }

    override fun toString(): String {
        return "socio: ${this.id}, ${this.nome}, limite: ${this.limite}, emprestados: ${this.qtdEmprestados()}"
    }
}

class Biblioteca {
    private val socios: MutableMap<String, Socio> = linkedMapOf()
    private val livros: MutableMap<String, Livro> = linkedMapOf()
    private val emprestimos: MutableMap<String, String> = mutableMapOf()

    fun cadastrarSocio(id: String, nome: String, limite: Int): Unit {
        if (this.socios.containsKey(id)) {
            throw IllegalArgumentException("socio already exists")
        }
        val novoSocio: Socio = Socio(id, nome, limite)
        this.socios[id] = novoSocio
    }

    fun cadastrarLivro(id: String, titulo: String): Unit {
        if (this.livros.containsKey(id)) {
            throw IllegalArgumentException("book already exists")
        }
        val novoLivro: Livro = Livro(id, titulo)
        this.livros[id] = novoLivro
    }

    fun emprestar(socioId: String, livroId: String): Unit {
        val socio: Socio = this.socios[socioId] ?: throw IllegalArgumentException("socio not found")
        val livro: Livro = this.livros[livroId] ?: throw IllegalArgumentException("book not found")

        // Validação prévia de disponibilidade para garantir atomicidade/integridade
        if (!livro.isDisponivel()) {
            throw IllegalStateException("book not available")
        }
        if (socio.qtdEmprestados() >= socio.getLimite()) {
            throw IllegalStateException("socio reached loan limit")
        }

        livro.emprestar()
        socio.adicionarLivro(livro)
        this.emprestimos[livroId] = socioId
    }

    fun devolver(livroId: String): Unit {
        val livro: Livro = this.livros[livroId] ?: throw IllegalArgumentException("book not found")
        if (livro.isDisponivel() || !this.emprestimos.containsKey(livroId)) {
            throw IllegalStateException("book not loaned")
        }

        val socioId: String = this.emprestimos[livroId]!!
        val socio: Socio = this.socios[socioId]!!

        socio.removerLivro(livroId)
        livro.devolver()
        this.emprestimos.remove(livroId)
    }

    override fun toString(): String {
        val sb: StringBuilder = StringBuilder()
        for (socio: Socio in this.socios.values) {
            sb.append(socio.toString()).append("\n")
        }
        val livrosValues: Collection<Livro> = this.livros.values
        val iterator: Iterator<Livro> = livrosValues.iterator()
        while (iterator.hasNext()) {
            val livro: Livro = iterator.next()
            sb.append(livro.toString())
            if (iterator.hasNext()) {
                sb.append("\n")
            }
        }
        return sb.toString()
    }
}

fun main(): Unit {
    val biblioteca: Biblioteca = Biblioteca()

    while (true) {
        val line: String = readLine() ?: break
        println("$" + line)

        val parts: List<String> = line.trim().split(Regex("\\s+"))
        when (parts[0]) {
            "end" -> break
            "add_socio" -> {
                try {
                    biblioteca.cadastrarSocio(parts[1], parts[2], parts[3].toInt())
                } catch (e: Exception) {
                    println("fail: ${e.message}")
                }
            }
            "add_livro" -> {
                try {
                    biblioteca.cadastrarLivro(parts[1], parts[2])
                } catch (e: Exception) {
                    println("fail: ${e.message}")
                }
            }
            "emprestar" -> {
                try {
                    biblioteca.emprestar(parts[1], parts[2])
                } catch (e: Exception) {
                    println("fail: ${e.message}")
                }
            }
            "devolver" -> {
                try {
                    biblioteca.devolver(parts[1])
                } catch (e: Exception) {
                    println("fail: ${e.message}")
                }
            }
            "show" -> println(biblioteca)
            else -> println(INVALID_COMMAND_MSG)
        }
    }
}