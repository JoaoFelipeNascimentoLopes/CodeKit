import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os

class AdminSeeder(ctk.CTkFrame):
    def __init__(self, master, db, on_finish, **kwargs):
        super().__init__(master, fg_color="#1E293B", **kwargs)
        self.db = db
        self.on_finish = on_finish

        # UI Center Layout
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.content, text="🛠️ ADMIN SEEDER MODE", 
                    font=("Arial", 32, "bold"), text_color="#10B981").pack(pady=20)
        
        ctk.CTkLabel(self.content, 
                    text="Use esta ferramenta para importar snippets que serão\nmarcados como PADRÃO do sistema.", 
                    font=("Arial", 16), text_color="#94A3B8").pack(pady=10)

        self.btn_import = ctk.CTkButton(
            self.content, text="Selecionar Snippets em Lote (.codekit)", 
            command=self._bulk_import, height=60, width=400, 
            fg_color="#10B981", hover_color="#059669",
            font=("Arial", 16, "bold"), cursor="hand2"
        )
        self.btn_import.pack(pady=30)

        self.status_label = ctk.CTkLabel(self.content, text="Status: Aguardando seleção...", 
                                        font=("Arial", 14), text_color="#F1F5F9")
        self.status_label.pack(pady=10)

        ctk.CTkButton(self.content, text="Sair do Modo Dev e Abrir App", 
                     command=on_finish, fg_color="transparent", 
                     border_width=1, text_color="#94A3B8", height=40).pack(pady=40)

    def _bulk_import(self):
        paths = filedialog.askopenfilenames(
            title="Importar Snippets de Sistema",
            filetypes=[("CodeKit Files", "*.codekit"), ("JSON Files", "*.json")]
        )
        
        if paths:
            count = 0
            errors = 0
            for path in paths:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # Verificação flexível de chaves (ajusta se vier 'code' ou 'code_content')
                    category = data.get("category")
                    title = data.get("title")
                    language = data.get("language")
                    code = data.get("code") or data.get("code_content")
                    version = data.get("version", "")

                    if all([category, title, language, code]):
                        # Chama o método de inserção de sistema (PADRÃO)
                        self.db.add_default_snippet(
                            category, 
                            title, 
                            language, 
                            code, 
                            version
                        )
                        count += 1
                    else:
                        print(f"⚠️ Campos faltando no arquivo: {os.path.basename(path)}")
                        errors += 1
                        
                except Exception as e:
                    print(f"❌ Falha ao processar {path}: {str(e)}")
                    errors += 1

            if count > 0:
                messagebox.showinfo("Sucesso", f"Semeadura Concluída!\n{count} snippets adicionados como PADRÃO.")
            
            if errors > 0:
                messagebox.showwarning("Aviso", f"{errors} arquivos falharam. Verifique o terminal para detalhes.")
                
            self.status_label.configure(text=f"Status: {count} injetados | {errors} falhas.")