const val INVALID_COMMAND_MSG: String = "fail: invalid command"

class Livro(private val id: String = "", private val titulo: String = "") {
    private var disponivel: Boolean = true

    fun getId(): String {
        TODO("retorne o id do livro")
    }

    fun getTitulo(): String {
        TODO("retorne o titulo do livro")
    }

    fun isDisponivel(): Boolean {
        TODO("retorne se o livro esta disponivel")
    }

    fun emprestar(): Unit {
        TODO("torne o livro indisponivel; lance IllegalStateException se ja indisponivel")
    }

    fun devolver(): Unit {
        TODO("torne o livro disponivel; lance IllegalStateException se ja disponivel")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do livro")
    }
}

class Socio(private val id: String = "", private val nome: String = "", private var limite: Int = 0) {
    private val livrosEmprestados: MutableList<Livro> = mutableListOf()

    init {
        // TODO: valide o limite (maior que 0) e inicialize os atributos
    }

    fun getId(): String {
        TODO("retorne o id do socio")
    }

    fun getNome(): String {
        TODO("retorne o nome do socio")
    }

    fun getLimite(): Int {
        TODO("retorne o limite de emprestimos do socio")
    }

    fun adicionarLivro(livro: Livro): Unit {
        TODO("adicione o livro a lista de emprestados; lance IllegalStateException se atingiu o limite")
    }

    fun removerLivro(livroId: String): Boolean {
        TODO("remova o livro da lista de emprestados pelo id; retorne true se removido ou false se nao estava")
    }

    fun qtdEmprestados(): Int {
        TODO("retorne a quantidade de livros emprestados")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual do socio")
    }
}

class Biblioteca {
    private val socios: MutableMap<String, Socio> = mutableMapOf()
    private val livros: MutableMap<String, Livro> = mutableMapOf()
    private val emprestimos: MutableMap<String, String> = mutableMapOf()

    fun cadastrarSocio(id: String, nome: String, limite: Int): Unit {
        TODO("cadastre um novo socio no mapa; lance IllegalArgumentException se ja existir")
    }

    fun cadastrarLivro(id: String, titulo: String): Unit {
        TODO("cadastre um novo livro no mapa; lance IllegalArgumentException se ja existir")
    }

    fun emprestar(socioId: String, livroId: String): Unit {
        TODO("empreste o livro para o socio; lance excecoes apropriadas se nao existir, livro indisponivel ou limite atingido")
    }

    fun devolver(livroId: String): Unit {
        TODO("devolva o livro emprestado; lance excecoes apropriadas se nao existir ou nao estiver emprestado")
    }

    override fun toString(): String {
        TODO("retorne a representacao textual de todos os socios e livros cadastrados")
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