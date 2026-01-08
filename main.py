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

# Importação da tela de Seeder para o Modo Dev
from ui.admin_seeder import AdminSeeder 

# CONFIGURAÇÃO DE DESENVOLVEDOR: 
IS_DEV_MODE = False

def resource_path(relative_path):
    """ Obtém o caminho absoluto para os recursos, necessário para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_db_path():
    """ Define o local do banco de dados na pasta AppData para evitar erros de permissão no Windows """
    if getattr(sys, 'frozen', False):
        # Caminho em produção: C:\Users\Nome\AppData\Roaming\CodeKit\codekit.db
        app_data_dir = os.path.join(os.environ.get('APPDATA'), 'CodeKit')
    else:
        # Caminho em desenvolvimento: pasta local
        app_data_dir = os.path.abspath(".")
    
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
        
    return os.path.join(app_data_dir, "codekit.db")

# --- CLASSE: ASSISTENTE DE IMPORTAÇÃO SELETIVA COM CONTADORES ---
class ImportWizard(ctk.CTkToplevel):
    def __init__(self, parent, folder_path, files, on_confirm):
        super().__init__(parent)
        self.title("CodeKit - Assistente de Sincronização")
        self.geometry("550x700")
        
        # Manter no topo durante a seleção
        self.attributes("-topmost", True)
        
        self.on_confirm = on_confirm
        self.folder_path = folder_path
        self.files = files
        self.checkboxes = []

        self.configure(fg_color="#F3F4F6")
        
        # Centralizar Modal
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

        # Título e Contador Dinâmico
        ctk.CTkLabel(self, text="📥 Sincronização de Kits", font=("Arial", 22, "bold"), text_color="#1E293B").pack(pady=(20, 5))
        
        self.counter_label = ctk.CTkLabel(self, text="", font=("Arial", 14, "bold"), text_color="#3B82F6")
        self.counter_label.pack(pady=5)
        
        info_text = (
            "Os itens selecionados serão integrados como snippets 'Padrão'.\n"
            "Eles não podem ser editados ou excluídos individualmente após o salvamento."
        )
        ctk.CTkLabel(self, text=info_text, font=("Arial", 12), text_color="#64748B", wraplength=480).pack(pady=5)

        # Botões de Seleção Rápida
        link_frame = ctk.CTkFrame(self, fg_color="transparent")
        link_frame.pack(fill="x", padx=40)
        
        ctk.CTkButton(link_frame, text="Marcar Todos", font=("Arial", 11, "underline"), fg_color="transparent", 
                      hover=False, text_color="#3B82F6", width=80, command=self._select_all).pack(side="left")
        ctk.CTkButton(link_frame, text="Desmarcar Todos", font=("Arial", 11, "underline"), fg_color="transparent", 
                      hover=False, text_color="#64748B", width=80, command=self._deselect_all).pack(side="left", padx=10)

        # Scrollable Frame
        self.scroll = ctk.CTkScrollableFrame(self, width=480, height=350, fg_color="white", border_width=1, border_color="#E2E8F0")
        self.scroll.pack(pady=10, padx=20)

        for file in self.files:
            display_name = file.replace(".codekit", "").replace("_", " ").title()
            cb = ctk.CTkCheckBox(self.scroll, text=display_name, font=("Arial", 13), text_color="#1E293B", command=self._update_counter)
            cb.pack(anchor="w", pady=8, padx=10)
            cb.select()
            self.checkboxes.append((cb, file))

        self._update_counter()

        # Botões de Ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=30, padx=40)

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#E2E8F0", text_color="#475569", hover_color="#CBD5E1", 
                      command=self.destroy).pack(side="left", expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="Confirmar Importação", fg_color="#3B82F6", hover_color="#2563EB", 
                      command=self._handle_confirm).pack(side="right", expand=True, padx=10)

    def _update_counter(self):
        total_selected = sum(1 for cb, _ in self.checkboxes if cb.get() == 1)
        self.counter_label.configure(text=f"{total_selected} de {len(self.files)} snippets selecionados")

    def _select_all(self):
        for cb, _ in self.checkboxes: cb.select()
        self._update_counter()

    def _deselect_all(self):
        for cb, _ in self.checkboxes: cb.deselect()
        self._update_counter()

    def _handle_confirm(self):
        selected_files = [file for cb, file in self.checkboxes if cb.get() == 1]
        if not selected_files:
            messagebox.showwarning("Aviso", "Selecione ao menos um snippet para importar.")
            return
        
        self.attributes("-topmost", False)
        self.withdraw()
        self.on_confirm(self.folder_path, selected_files)
        self.destroy()

# --- CLASSE PRINCIPAL ---
class CodeKitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.wizard_instance = None 

        icon_path = resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            try: self.iconbitmap(icon_path)
            except Exception as e: print(f"Erro ao carregar bitmap: {e}")
        
        self.width = 1280
        self.height = 720
        self.title("CodeKit - Gestor de Snippets")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self._center_window()
        self.configure(fg_color=COLOR_BG)
        
        # Inicializa o banco de dados em um local com permissão de escrita
        self.db = Database(db_name=get_db_path())
        self.share_manager = ShareManager(self.db)
        
        self.kit_colors = {
            "Documentos": "#3498db", "Matemática": "#2ecc71", "Strings": "#e67e22",
            "Datas": "#9b59b6", "Arrays": "#f1c40f", "Arquivos": "#e74c3c",
            "Redes": "#1abc9c", "Segurança": "#34495e", "Utilitários": "#f1c40f", 
            "Algoritmos": "#d35400", "Meus Snippets": "#FF8911"
        }
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        if IS_DEV_MODE: self.show_admin_seeder()
        else: self.show_dashboard()

    def _center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"+{x}+{y}")

    def show_admin_seeder(self):
        for child in self.container.winfo_children(): child.destroy()
        self.seeder = AdminSeeder(self.container, self.db, self.show_dashboard)
        self.seeder.pack(fill="both", expand=True)

    def show_dashboard(self):
        for child in self.container.winfo_children(): child.destroy()
        
        all_categories = self.db.get_categories()
        filtered_categories = [c for c in all_categories if c[1] != "Meus Snippets"]
        
        self.dashboard = DashboardScreen(
            self.container, 
            categories=filtered_categories,
            on_category_select=self.open_kit,
            on_create_new=lambda: self.open_kit("Meus Snippets"),
            on_sync_kits=self.start_sync_wizard 
        )
        self.dashboard.pack(fill="both", expand=True)

        total = self.db.get_total_snippets_count()
        footer = ctk.CTkFrame(self.container, fg_color="transparent", height=30)
        footer.pack(side="bottom", fill="x", padx=20, pady=10)
        ctk.CTkLabel(footer, text=f"Total de Snippets Salvos: {total}", font=("Arial", 11), text_color="#94A3B8").pack(side="right")

    def start_sync_wizard(self):
        folder_path = filedialog.askdirectory(title="Selecione a pasta de atualização (Kits Padrão)")
        if not folder_path: return
        files = [f for f in os.listdir(folder_path) if f.endswith('.codekit')]
        if not files:
            messagebox.showwarning("Aviso", "Nenhum arquivo .codekit encontrado.")
            return
        
        self.wizard_instance = ImportWizard(self, folder_path, files, self.process_sync_import)

    def process_sync_import(self, folder_path, selected_files):
        count = 0
        for file_name in selected_files:
            # Uso de path absoluto para garantir que o .exe encontre os arquivos
            full_file_path = os.path.join(folder_path, file_name)
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.db.update_system_snippets(
                        category_name=data.get('category', 'Utilitários'),
                        title=data['title'], language=data['language'],
                        code=data['code'], version=data.get('version', '1.0')
                    )
                    count += 1
            except Exception as e: print(f"Erro em {file_name}: {e}")
        
        self.update() 
        self.focus_force()
        messagebox.showinfo("Sucesso", f"Sincronização concluída!\n{count} snippets adicionados.", parent=self)
        self.show_dashboard()

    def open_kit(self, category_name):
        snippets = self.db.get_snippets_by_category(category_name)
        all_categories = self.db.get_categories()
        category_icon = "📂" 
        for cat in all_categories:
            if cat[1] == category_name:
                category_icon = cat[2]
                break
        
        category_color = self.kit_colors.get(category_name, "#1E293B")
        for child in self.container.winfo_children(): child.destroy()

        self.viewer = SnippetViewer(
            self.container, category_name=category_name, category_icon=category_icon,
            category_color=category_color, snippets=snippets, on_back=self.show_dashboard,
            on_export=self.share_manager.export_snippet, on_add_new=self.open_creation_options,
            on_edit=self.open_edit_dialog, on_delete=self.handle_delete, is_dev_mode=IS_DEV_MODE 
        )
        self.viewer.pack(fill="both", expand=True)

    def open_creation_options(self):
        CreationDialog(master=self, categories=self.db.get_categories(), on_save=self.save_new_snippet)

    def open_edit_dialog(self, snippet_data):
        CreationDialog(master=self, categories=self.db.get_categories(), 
                       on_save=lambda cat, t, l, c, v: self.save_edit(snippet_data[0], cat, t, l, c, v),
                       edit_mode=True, initial_data=snippet_data)

    def save_new_snippet(self, category, title, lang, code, version):
        self.db.add_custom_snippet(category, title, lang, code, version)
        self.open_kit(category)

    def save_edit(self, s_id, category, title, lang, code, version):
        if s_id is None: self.db.add_custom_snippet(category, title, lang, code, version)
        else: self.db.update_snippet(s_id, category, title, lang, code, version)
        self.open_kit(category)

    def handle_delete(self, snippet_id, category_name):
        self.db.delete_snippet(snippet_id)
        self.open_kit(category_name)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = CodeKitApp()
    app.mainloop()