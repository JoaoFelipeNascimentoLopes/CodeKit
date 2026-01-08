import json
from tkinter import filedialog, messagebox

class ShareManager:
    def __init__(self, db_instance):
        """Recebe a instância da classe Database para interagir com o SQLite."""
        self.db = db_instance

    def export_snippet(self, snippet_id):
        """
        Extrai um snippet do banco de dados e guarda-o num ficheiro .codekit.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT s.title, s.language, s.code_content, c.name 
            FROM snippets s 
            JOIN categories c ON s.category_id = c.id 
            WHERE s.id = ?
        """
        cursor.execute(query, (snippet_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False

        # Estrutura os dados para o ficheiro de partilha
        data_to_export = {
            "title": row[0],
            "language": row[1],
            "code": row[2],
            "category_origin": row[3]
        }
        
        # Abre a janela para o utilizador escolher onde guardar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".codekit",
            filetypes=[("CodeKit File", "*.codekit")],
            initialfile=f"{row[0].replace(' ', '_')}.codekit"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_export, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Erro ao exportar: {e}")
        return False

    def import_snippet(self):
        """
        Abre um ficheiro .codekit e regista o conteúdo no banco de dados local.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("CodeKit File", "*.codekit")]
        )
        
        if not file_path:
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Validação básica de campos obrigatórios
            required_fields = ["title", "language", "code", "category_origin"]
            if not all(field in imported_data for field in required_fields):
                raise ValueError("Formato de ficheiro .codekit inválido.")

            # Utiliza o método add_custom_snippet da nossa Database
            self.db.add_custom_snippet(
                category_name=imported_data["category_origin"],
                title=imported_data["title"],
                language=imported_data["language"],
                code=imported_data["code"]
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro de Importação", f"Não foi possível ler o ficheiro: {e}")
            return False