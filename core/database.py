import sqlite3
import os

class Database:
    def __init__(self, db_name="codekit.db"):
        self.db_name = db_name
        self.init_db()
        self._upgrade_db() 

    def get_connection(self):
        """Retorna uma conexão e ativa suporte a chaves estrangeiras."""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Cria as tabelas caso não existam."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    icon TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    title TEXT NOT NULL,
                    language TEXT NOT NULL,
                    code_content TEXT NOT NULL,
                    version TEXT DEFAULT '',
                    is_custom INTEGER DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

            conn.commit()
            self._seed_initial_data(cursor, conn)

    def _upgrade_db(self):
        """Adiciona colunas novas sem apagar dados existentes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE snippets ADD COLUMN version TEXT DEFAULT ''")
            except sqlite3.OperationalError: pass
            
            try:
                cursor.execute("ALTER TABLE snippets ADD COLUMN is_custom INTEGER DEFAULT 0")
            except sqlite3.OperationalError: pass
            
            conn.commit()

    def _seed_initial_data(self, cursor, conn):
        """Popula as categorias iniciais."""
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            kits = [
                ("Documentos", "📄"), ("Matemática", "🔢"), ("Strings", "🔤"),
                ("Datas", "📅"), ("Arrays", "📊"), ("Arquivos", "📁"),
                ("Redes", "🌐"), ("Segurança", "🔒"), ("Utilitários", "⚡"),
                ("Algoritmos", "🧠"), ("Meus Snippets", "📂")
            ]
            for name, icon in kits:
                cursor.execute("INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)", (name, icon))
            conn.commit()

    def get_categories(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, icon FROM categories")
            return cursor.fetchall()

    def get_snippets_by_category(self, category_name):
        """Retorna snippets com o nome da categoria incluído na posição [7]."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category_name == "Meus Snippets":
                query = """
                    SELECT s.id, s.category_id, s.title, s.language, s.code_content, s.version, s.is_custom, c.name
                    FROM snippets s
                    JOIN categories c ON s.category_id = c.id
                    WHERE s.is_custom = 1
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT s.id, s.category_id, s.title, s.language, s.code_content, s.version, s.is_custom, c.name
                    FROM snippets s
                    JOIN categories c ON s.category_id = c.id
                    WHERE c.name = ?
                """
                cursor.execute(query, (category_name,))
            return cursor.fetchall()

    def add_custom_snippet(self, category_name, title, language, code, version=""):
        """Adiciona snippet do USUÁRIO (is_custom = 1)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            res = cursor.fetchone()
            
            if not res or category_name == "Meus Snippets":
                cat_id = self._get_meus_snippets_id(cursor)
            else:
                cat_id = res[0]
            
            cursor.execute('''
                INSERT INTO snippets (category_id, title, language, code_content, version, is_custom)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (cat_id, title, language, code, version))
            conn.commit()

    def add_default_snippet(self, category_name, title, language, code, version=""):
        """MÉTODO PARA O SEEDER: Adiciona snippet de SISTEMA (is_custom = 0)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            res = cursor.fetchone()
            
            if res:
                cat_id = res[0]
            else:
                cursor.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (category_name, "📁"))
                cat_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO snippets (category_id, title, language, code_content, version, is_custom)
                VALUES (?, ?, ?, ?, ?, 0)
            ''', (cat_id, title, language, code, version))
            conn.commit()

    def update_system_snippets(self, category_name, title, language, code, version=""):
        """
        Lógica para Sincronização de Kits (GitHub/Pasta).
        Atualiza snippets padrão existentes ou cria novos sem mexer nos 'Custom'.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Busca ou cria a categoria
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            res = cursor.fetchone()
            if res:
                cat_id = res[0]
            else:
                cursor.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (category_name, "📁"))
                cat_id = cursor.lastrowid

            # 2. Tenta atualizar se já existir um snippet de SISTEMA (is_custom=0) com esse título
            cursor.execute('''
                UPDATE snippets 
                SET code_content = ?, version = ?, language = ?
                WHERE category_id = ? AND title = ? AND is_custom = 0
            ''', (code, version, language, cat_id, title))

            # 3. Se não existia nenhum PADRÃO com esse nome, insere como novo de sistema
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO snippets (category_id, title, language, code_content, version, is_custom)
                    VALUES (?, ?, ?, ?, ?, 0)
                ''', (cat_id, title, language, code, version))
            
            conn.commit()

    def _get_meus_snippets_id(self, cursor):
        cursor.execute("SELECT id FROM categories WHERE name = 'Meus Snippets'")
        res = cursor.fetchone()
        return res[0] if res else 1

    def update_snippet(self, snippet_id, category_name, title, language, code, version):
        """Atualiza o snippet, permitindo inclusive trocar a categoria (Pasta)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            res = cursor.fetchone()
            
            if not res or category_name == "Meus Snippets":
                cat_id = self._get_meus_snippets_id(cursor)
            else:
                cat_id = res[0]

            cursor.execute('''
                UPDATE snippets 
                SET category_id = ?, title = ?, language = ?, code_content = ?, version = ?
                WHERE id = ?
            ''', (cat_id, title, language, code, version, snippet_id))
            conn.commit()

    def delete_snippet(self, snippet_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
            conn.commit()
    
    def search_all_snippets(self, query):
        """Busca global em todos os snippets cadastrados."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_query = f"%{query}%"
            sql = """
                SELECT s.id, s.category_id, s.title, s.language, s.code_content, s.version, s.is_custom, c.name
                FROM snippets s
                JOIN categories c ON s.category_id = c.id
                WHERE s.title LIKE ? OR s.code_content LIKE ? OR s.language LIKE ?
                ORDER BY s.is_custom DESC, s.title ASC
            """
            cursor.execute(sql, (search_query, search_query, search_query))
            return cursor.fetchall()

    def get_total_snippets_count(self):
        """Retorna a contagem total de todos os snippets armazenados no banco."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM snippets")
            result = cursor.fetchone()
            return result[0] if result else 0