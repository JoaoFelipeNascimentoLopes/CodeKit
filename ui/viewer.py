import customtkinter as ctk
from ui.styles import *
from core.highlighter import SyntaxHighlighter 
from tkinter import filedialog, messagebox
import json 

try:
    import pyperclip
except ImportError:
    pyperclip = None

class SnippetViewer(ctk.CTkFrame):
    def __init__(self, master, category_name, category_icon, category_color, snippets, on_back, on_export, 
                 on_add_new=None, on_edit=None, on_delete=None, is_dev_mode=False, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)
        
        self.snippets = snippets 
        self.category_name = category_name
        self.category_icon = category_icon 
        self.category_color = category_color 
        self.on_export = on_export
        self.on_add_new = on_add_new
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.is_dev_mode = is_dev_mode 
        self.highlighter = SyntaxHighlighter()
        
        # --- HEADER ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=30, pady=25)
        
        self.back_btn = ctk.CTkButton(
            self.top_bar, text="← Voltar", width=100, height=35,
            fg_color="#F1F5F9", text_color="#475569", hover_color="#E2E8F0",
            command=on_back, corner_radius=12, cursor="hand2", font=(FONT_FAMILY, 13, "bold")
        )
        self.back_btn.pack(side="left")
        
        self.title_container = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.title_container.pack(side="left", padx=25)

        self.icon_label = ctk.CTkLabel(self.title_container, text=self.category_icon, font=(FONT_FAMILY, 34), text_color=self.category_color)
        self.icon_label.pack(side="left")

        self.title_label = ctk.CTkLabel(self.title_container, text=category_name, font=(FONT_FAMILY, 26, "bold"), text_color=COLOR_TEXT_MAIN)
        self.title_label.pack(side="left", padx=15, pady=(2, 0))

        if self.on_add_new:
            self.import_btn = ctk.CTkButton(
                self.top_bar, text="📥 Importar Snippet", width=130, height=38,
                fg_color="#10B981", hover_color="#059669", text_color="white",
                command=self._trigger_import, corner_radius=12, cursor="hand2", font=(FONT_FAMILY, 13, "bold")
            )
            self.import_btn.pack(side="right", padx=8)

            self.add_btn = ctk.CTkButton(
                self.top_bar, text="+ Novo Snippet", width=140, height=38,
                fg_color=COLOR_ACCENT, hover_color="#1D4ED8",
                command=self.on_add_new, corner_radius=12, cursor="hand2", font=(FONT_FAMILY, 13, "bold")
            )
            self.add_btn.pack(side="right", padx=8)

        # --- LAYOUT PRINCIPAL ---
        self.content_layout = ctk.CTkFrame(self, fg_color="transparent")
        self.content_layout.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Painel Esquerdo (Largo: 420px)
        self.left_panel = ctk.CTkFrame(self.content_layout, fg_color="transparent", width=420)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        self.left_panel.pack_propagate(False)

        # Barra de Pesquisa
        self.search_entry = ctk.CTkEntry(
            self.left_panel, placeholder_text="🔍 Buscar nesta categoria...",
            height=35, corner_radius=10, border_width=1, font=(FONT_FAMILY, 12)
        )
        self.search_entry.pack(fill="x", pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._filter_snippets)

        # Lista Lateral (Scrollable)
        self.side_list = ctk.CTkScrollableFrame(
            self.left_panel, fg_color=COLOR_CARD, 
            corner_radius=20, border_width=1, border_color="#E2E8F0"
        )
        self.side_list.pack(fill="both", expand=True)

        # Container da Direita (Editor de Código)
        self.code_container = ctk.CTkFrame(
            self.content_layout, fg_color=COLOR_CARD, corner_radius=25, 
            border_width=1, border_color="#E2E8F0"
        )
        self.code_container.pack(side="right", fill="both", expand=True)
        
        # --- CABEÇALHO DO EDITOR (Título + Tag de Linguagem) ---
        self.code_header = ctk.CTkFrame(self.code_container, fg_color="transparent")
        self.code_header.pack(fill="x", padx=25, pady=(25, 0))
        
        self.current_snip_label = ctk.CTkLabel(self.code_header, text="Selecione um snippet", font=(FONT_FAMILY, 18, "bold"), text_color="#1E293B")
        self.current_snip_label.pack(side="left")

        self.lang_tag = ctk.CTkLabel(
            self.code_header, text="", font=(FONT_FAMILY, 10, "bold"),
            width=80, height=22, fg_color="#F1F5F9", text_color="#475569", corner_radius=6
        )
        self.lang_tag.pack(side="left", padx=15)
        self.lang_tag.pack_forget() # Inicia escondida

        # Rodapé de Ações
        self.action_bar = ctk.CTkFrame(self.code_container, fg_color="#F8FAFC", height=70, corner_radius=0)
        self.action_bar.pack(fill="x", side="bottom")
        self.action_bar.pack_propagate(False)

        self.management_btns = ctk.CTkFrame(self.action_bar, fg_color="transparent")
        self.management_btns.pack(side="left", padx=20)

        self.edit_btn = ctk.CTkButton(self.management_btns, text="✏️ Editar", width=90, height=32, fg_color="#FDE68A", text_color="#92400E", command=self._trigger_edit, corner_radius=8, font=(FONT_FAMILY, 11, "bold"))
        self.delete_btn = ctk.CTkButton(self.management_btns, text="🗑️ Excluir", width=90, height=32, fg_color="#FEE2E2", text_color="#B91C1C", command=self._trigger_delete, corner_radius=8, font=(FONT_FAMILY, 11, "bold"))

        self.export_btn = ctk.CTkButton(self.action_bar, text="📤 Exportar", width=120, height=36, fg_color="transparent", text_color="#475569", border_width=1, border_color="#CBD5E1", command=self._trigger_export, corner_radius=10, font=(FONT_FAMILY, 12, "bold"))
        self.export_btn.pack(side="right", padx=(5, 20))

        self.copy_btn = ctk.CTkButton(self.action_bar, text="📋 Copiar Código", width=140, height=36, fg_color=COLOR_ACCENT, command=self._copy_to_clipboard, corner_radius=10, font=(FONT_FAMILY, 12, "bold"))
        self.copy_btn.pack(side="right", padx=5)

        # --- ÁREA DO EDITOR (ESTILO IDE) ---
        self.editor_wrapper = ctk.CTkFrame(self.code_container, fg_color="#0F172A", corner_radius=15)
        self.editor_wrapper.pack(fill="both", expand=True, padx=25, pady=25)

        self.line_numbers = ctk.CTkTextbox(
            self.editor_wrapper, width=45, font=("Consolas", 15), 
            fg_color="#070b14", text_color="#475569", border_width=0, corner_radius=0,
            activate_scrollbars=False 
        )
        self.line_numbers.pack(side="left", fill="y", padx=(5, 0), pady=10)
        self.line_numbers.configure(state="disabled")

        self.code_text = ctk.CTkTextbox(
            self.editor_wrapper, font=("Consolas", 15), 
            fg_color="transparent", text_color="#E2E8F0", border_width=0
        )
        self.code_text.pack(side="right", fill="both", expand=True, padx=5, pady=10)
        
        self.code_text._textbox.configure(yscrollcommand=self._sync_scroll)

        self._populate_list()

    def _sync_scroll(self, *args):
        self.line_numbers._textbox.yview_moveto(args[0])

    def _update_line_numbers(self):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        code_content = self.code_text.get("1.0", "end-1c")
        line_count = code_content.count('\n') + 1
        lines_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", lines_string)
        self.line_numbers._textbox.tag_add("right", "1.0", "end")
        self.line_numbers._textbox.tag_config("right", justify="right")
        self.line_numbers.configure(state="disabled")

    def _filter_snippets(self, event=None):
        query = self.search_entry.get().lower()
        for item_frame in self.side_list.winfo_children():
            btn = next((child for child in item_frame.winfo_children() if isinstance(child, ctk.CTkButton)), None)
            if btn:
                if query == "" or query in btn.cget("text").lower():
                    item_frame.pack(fill="x", pady=1, padx=5)
                else:
                    item_frame.pack_forget()

    def _populate_list(self):
        for child in self.side_list.winfo_children():
            child.destroy()
        for snip in self.snippets:
            is_custom = snip[6] if len(snip) > 6 else 0
            cat_origin = snip[7] if len(snip) > 7 else ""
            
            item_frame = ctk.CTkFrame(self.side_list, fg_color="transparent", height=35)
            item_frame.pack(fill="x", pady=2, padx=5) 
            item_frame.pack_propagate(False) 
            
            tag_text, tag_bg, tag_color = ("CUSTOM", "#E0F2FE", "#0369A1") if is_custom else ("PADRÃO", "#FFEDD5", "#C2410C")
            ctk.CTkLabel(item_frame, text=tag_text, font=(FONT_FAMILY, 8, "bold"), width=52, height=20, fg_color=tag_bg, text_color=tag_color, corner_radius=4).pack(side="left", padx=(5, 2))
            
            if self.category_name == "Meus Snippets":
                ctk.CTkLabel(item_frame, text=cat_origin.upper(), font=(FONT_FAMILY, 8, "bold"), width=70, height=20, fg_color="#F1F5F9", text_color="#64748B", corner_radius=4).pack(side="left", padx=2)

            ctk.CTkButton(
                item_frame, text=f"{snip[3].upper()} • {snip[2]}", anchor="w", 
                fg_color="transparent", text_color=COLOR_TEXT_MAIN, hover_color="#F1F5F9", height=30, 
                font=(FONT_FAMILY, 11, "bold" if is_custom else "normal"), 
                command=lambda s=snip: self._display_code(s)
            ).pack(side="left", fill="both", expand=True, padx=2)

    def _display_code(self, snippet_data):
        self.current_snippet = snippet_data
        self.current_snip_label.configure(text=snippet_data[2])
        
        # Atualiza a Tag de Linguagem no Header do Editor
        self.lang_tag.pack(side="left", padx=15)
        self.lang_tag.configure(text=snippet_data[3].upper())

        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", snippet_data[4])
        self._update_line_numbers()
        self.highlighter.apply_highlight(text_widget=self.code_text, code=snippet_data[4], lang_name=snippet_data[3])
        self.code_text.configure(state="disabled")
        
        is_custom = snippet_data[6] if len(snippet_data) > 6 else 0
        if is_custom or self.is_dev_mode:
            self.edit_btn.pack(side="left", padx=5)
            self.delete_btn.pack(side="left", padx=5)
            if not is_custom: self.edit_btn.pack_forget() 
        else:
            self.edit_btn.pack_forget()
            self.delete_btn.pack_forget()

    def _copy_to_clipboard(self):
        if not pyperclip: return
        code = self.code_text.get("1.0", "end-1c")
        if code.strip():
            pyperclip.copy(code)
            self.copy_btn.configure(text="✅ Copiado!", fg_color="#10B981")
            self.after(2000, lambda: self.copy_btn.configure(text="📋 Copiar Código", fg_color=COLOR_ACCENT))

    def _trigger_export(self):
        if hasattr(self, 'current_snippet'):
            cat_to_export = self.current_snippet[7] if len(self.current_snippet) > 7 else self.category_name
            export_data = {
                "title": self.current_snippet[2], 
                "language": self.current_snippet[3], 
                "code": self.current_snippet[4], 
                "version": self.current_snippet[5], 
                "category": cat_to_export
            }
            path = filedialog.asksaveasfilename(defaultextension=".codekit", initialfile=f"{self.current_snippet[2]}.codekit", filetypes=[("CodeKit Files", "*.codekit")])
            if path:
                with open(path, "w", encoding="utf-8") as f: json.dump(export_data, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Sucesso", "Exportado!")

    def _trigger_import(self):
        path = filedialog.askopenfilename(filetypes=[("CodeKit Files", "*.codekit"), ("JSON Files", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f: data = json.load(f)
            if all(k in data for k in ["title", "language", "code"]):
                import_data = (None, None, data["title"], data["language"], data["code"], data.get("version", ""), 1)
                if self.on_edit: self.on_edit(import_data)

    def _trigger_edit(self):
        if hasattr(self, 'current_snippet') and self.on_edit: self.on_edit(self.current_snippet)

    def _trigger_delete(self):
        if hasattr(self, 'current_snippet') and self.on_delete:
            if messagebox.askyesno("Excluir", f"Deseja excluir '{self.current_snippet[2]}'?"):
                self.on_delete(self.current_snippet[0], self.category_name)