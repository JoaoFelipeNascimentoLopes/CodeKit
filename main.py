import customtkinter as ctk
from core.database import Database
from core.share_manager import ShareManager
from ui.dashboard import DashboardScreen
from ui.viewer import SnippetViewer
from ui.creation_dialog import CreationDialog
from ui.styles import COLOR_BG
from tkinter import filedialog, messagebox
import json
import os
import sys

def resource_path(relative_path):
    """ Obtém o caminho absoluto para os recursos, necessário para PyInstaller """
    try:
        # Caminho temporário criado pelo PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CodeKitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÃO DE ÍCONE (Correção do Erro) ---
        icon_path = resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Erro ao carregar bitmap: {e}")
        
        # --- Configuração de Janela Fixa (1280x720) ---
        self.width = 1280
        self.height = 720
        self.title("CodeKit - Gestor de Snippets")
        
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self._center_window()
        
        self.configure(fg_color=COLOR_BG)
        
        # --- Inicialização do Backend ---
        self.db = Database()
        self.share_manager = ShareManager(self.db)
        
        # Mapa Global de Cores para Identidade Visual
        self.kit_colors = {
            "Documentos": "#3498db", "Matemática": "#2ecc71", "Strings": "#e67e22",
            "Datas": "#9b59b6", "Arrays": "#f1c40f", "Arquivos": "#e74c3c",
            "Redes": "#1abc9c", "Segurança": "#34495e", "Utilitários": "#f1c40f", 
            "Algoritmos": "#d35400", "Meus Snippets": "#FF8911"
        }
        
        # Container principal de telas
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        # Lógica de Inicialização Seletiva
        if IS_DEV_MODE:
            self.show_admin_seeder()
        else:
            self.show_dashboard()

    def _center_window(self):
        """Centraliza a aplicação na tela do usuário."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"+{x}+{y}")

    def show_admin_seeder(self):
        """Abre a ferramenta de importação em lote para o desenvolvedor."""
        for child in self.container.winfo_children():
            child.destroy()
        
        self.seeder = AdminSeeder(self.container, self.db, self.show_dashboard)
        self.seeder.pack(fill="both", expand=True)

    def show_dashboard(self):
        """Exibe a tela inicial de kits/categorias."""
        for child in self.container.winfo_children():
            child.destroy()
            
        all_categories = self.db.get_categories()
        filtered_categories = [c for c in all_categories if c[1] != "Meus Snippets"]
        
        self.dashboard = DashboardScreen(
            self.container, 
            categories=filtered_categories,
            on_category_select=self.open_kit,
            on_create_new=lambda: self.open_kit("Meus Snippets"),
            on_sync_kits=self.handle_sync_update 
        )
        self.dashboard.pack(fill="both", expand=True)

    def handle_sync_update(self):
        """Lógica para o usuário injetar uma pasta de códigos padrão baixada."""
        folder_path = filedialog.askdirectory(title="Selecione a pasta de atualização (Kits Padrão)")
        
        if not folder_path:
            return

        files = [f for f in os.listdir(folder_path) if f.endswith('.codekit')]
        
        if not files:
            messagebox.showwarning("Aviso", "Nenhum arquivo .codekit encontrado nesta pasta.")
            return

        count = 0
        for file in files:
            try:
                with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.db.update_system_snippets(
                        category_name=data.get('category', 'Utilitários'),
                        title=data['title'],
                        language=data['language'],
                        code=data['code'],
                        version=data.get('version', '1.0')
                    )
                    count += 1
            except Exception as e:
                print(f"Erro ao processar {file}: {e}")

        messagebox.showinfo("Sucesso", f"Sincronização concluída! {count} snippets de sistema atualizados.")
        self.show_dashboard() 

    def open_kit(self, category_name):
        """Busca os snippets, ícone e cor correspondente para abrir o viewer."""
        snippets = self.db.get_snippets_by_category(category_name)
        
        all_categories = self.db.get_categories()
        category_icon = "📂" 
        for cat in all_categories:
            if cat[1] == category_name:
                category_icon = cat[2]
                break
        
        category_color = self.kit_colors.get(category_name, "#1E293B")
        
        for child in self.container.winfo_children():
            child.destroy()

        self.viewer = SnippetViewer(
            self.container,
            category_name=category_name,
            category_icon=category_icon,
            category_color=category_color,
            snippets=snippets,
            on_back=self.show_dashboard,
            on_export=self.share_manager.export_snippet,
            on_add_new=self.open_creation_options,
            on_edit=self.open_edit_dialog,
            on_delete=self.handle_delete,
            is_dev_mode=IS_DEV_MODE 
        )
        self.viewer.pack(fill="both", expand=True)

    def open_creation_options(self):
        """Abre a IDE para criar um snippet NOVO."""
        CreationDialog(
            master=self,
            categories=self.db.get_categories(),
            on_save=self.save_new_snippet
        )

    def open_edit_dialog(self, snippet_data):
        """Abre a IDE para EDITAR ou para SALVAR IMPORTADO."""
        CreationDialog(
            master=self,
            categories=self.db.get_categories(),
            on_save=lambda cat, t, l, c, v: self.save_edit(snippet_data[0], cat, t, l, c, v),
            edit_mode=True,
            initial_data=snippet_data
        )

    def save_new_snippet(self, category, title, lang, code, version):
        """Salva um snippet criado do zero como CUSTOM."""
        self.db.add_custom_snippet(
            category_name=category, 
            title=title, 
            language=lang, 
            code=code, 
            version=version
        )
        self.open_kit(category)

    def save_edit(self, s_id, category, title, lang, code, version):
        """Lógica híbrida de salvamento para edições."""
        if s_id is None:
            self.db.add_custom_snippet(category, title, lang, code, version)
        else:
            self.db.update_snippet(s_id, category, title, lang, code, version)
    
        self.open_kit(category)

    def handle_delete(self, snippet_id, category_name):
        """Exclui o snippet e recarrega a visualização."""
        self.db.delete_snippet(snippet_id)
        self.open_kit(category_name)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = CodeKitApp()
    app.mainloop()