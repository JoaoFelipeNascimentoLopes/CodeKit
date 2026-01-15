# 🧊 CodeKit - Gestor de Snippets

O **CodeKit** é uma ferramenta de produtividade para desenvolvedores, projetada para organizar, centralizar e acessar rapidamente blocos de código (snippets). Construído com uma interface elegante e busca potente, o CodeKit elimina a necessidade de procurar lógicas repetitivas em projetos antigos, mantendo sua biblioteca sempre ao alcance de um clique.

⚠️ **Library Clean Mode:** O software é distribuído sem códigos pré-carregados. Você tem total liberdade para importar apenas os kits que desejar ou construir sua própria base de conhecimento.

---

## 🚀 Funcionalidades (Features)

* **Busca Global Inteligente:** Pesquise por título, linguagem ou conteúdo do código diretamente na Dashboard.
* **Tags de Identificação:** Visualize instantaneamente se o snippet é **Padão** ou **Custom**, além de sua categoria e linguagem.
* **Editor Estilo IDE:** Visualização com realce de sintaxe (Syntax Highlighting) e numeração de linhas.
* **Sincronização em Lote:** Importe pastas inteiras de snippets através do botão "Sincronizar Kits".
* **Gestão Autorais:** Aba dedicada "Meus Snippets" para você criar e gerenciar seus próprios códigos.
* **Exportação:** Salve snippets individualmente no formato `.codekit` para compartilhar com outros usuários.

---

## 🔧 Instalação (Windows)

1.  Acesse a página de [Releases](https://github.com/SEU_USUARIO/CodeKit/releases).
2.  Faça o download do arquivo `CodeKit_Instalador_vX.X.exe`.
3.  Execute o instalador e siga as instruções do assistente.
4.  O CodeKit estará disponível no seu Menu Iniciar e Área de Trabalho.

---

## 📦 Como carregar os Kits Oficiais

Para adicionar os snippets padrão ao seu CodeKit, siga estes passos:

1.  Na página de [Releases](https://github.com/SJoaoFelipeNascimentoLopes/CodeKit/releases), baixe o arquivo comprimido `Kits_Oficiais.zip`.
2.  Extraia a pasta em um local de sua preferência.
3.  Abra o **CodeKit** e, na tela inicial, clique no botão **🔄 Sincronizar Kits**.
4.  Selecione a pasta extraída.
5.  O software irá mapear as categorias e importar todos os arquivos `.codekit` automaticamente.

---

## 📂 Formato de Dados (.codekit)

O CodeKit utiliza arquivos JSON estruturados para garantir a portabilidade:

| Campo | Função |
| :--- | :--- |
| `title` | Título que aparecerá na listagem |
| `language` | Define o realce de sintaxe (ex: python, sql, cpp) |
| `code` | O conteúdo bruto do snippet |
| `category` | O Kit/Pasta onde o snippet será organizado |

---

## 🛠️ Tecnologias e Arquitetura

Este projeto foi desenvolvido utilizando:

* **Linguagem:** Python 3.12+
* **Interface:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Banco de Dados:** SQLite3
* **Highlighting:** Pygments
* **Instalador:** Inno Setup Compiler

---

## 💻 Autor e Contribuição

Desenvolvido com 🧊 por **João Felipe**.

Este é um projeto de código aberto! Sinta-se à vontade para explorar o código, abrir *Issues* ou enviar *Pull Requests* para melhorar o CodeKit.

📅 **Ano:** 2026
🚀 **Versão:** 1.0.0
