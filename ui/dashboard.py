import customtkinter as ctk
from ui.styles import *

class CategoryCard(ctk.CTkFrame):
    def __init__(self, master, name, icon, icon_color, command=None, **kwargs):
        super().__init__(
            master, 
            fg_color=COLOR_CARD, 
            corner_radius=25, 
            width=180, 
            height=180,
            cursor="hand2",
            **kwargs
        )
        
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.command = command
        
        # Ícone centralizado
        self.icon_label = ctk.CTkLabel(
            self, 
            text=icon, 
            font=(FONT_FAMILY, 52), 
            text_color=icon_color,
            cursor="hand2"
        )
        self.icon_label.place(relx=0.5, rely=0.45, anchor="center")

        # Nome do Kit
        self.name_label = ctk.CTkLabel(
            self, 
            text=name, 
            font=(FONT_FAMILY, 15, "bold"), 
            text_color=COLOR_TEXT_MAIN,
            cursor="hand2"
        )
        self.name_label.place(relx=0.5, rely=0.78, anchor="center")

        # Binds de clique
        for widget in [self, self.icon_label, self.name_label]:
            widget.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        self.configure(border_width=2, border_color=COLOR_ACCENT)
        self.after(100, lambda: self.configure(border_width=0))
        if self.command:
            self.command()

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, categories, on_category_select, on_create_new, on_sync_kits=None, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)
        
        self.on_sync_kits = on_sync_kits
        self.on_category_select = on_category_select
        
        self.kit_colors = {
            "Documentos": "#3498db", "Matemática": "#2ecc71", "Strings": "#e67e22",
            "Datas": "#9b59b6", "Arrays": "#f1c40f", "Arquivos": "#e74c3c",
            "Redes": "#1abc9c", "Segurança": "#34495e", "Utilitários": "#f1c40f", 
            "Algoritmos": "#d35400", "Meus Snippets": "#FF8911"
        }

        # --- CABEÇALHO ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=100, pady=(35, 15))

        self.logo_label = ctk.CTkLabel(self.header, text="🧊 CodeKit", font=(FONT_FAMILY, 28, "bold"), text_color="#1A365D")
        self.logo_label.pack(side="left")

        # BARRA DE PESQUISA GLOBAL
        self.search_global = ctk.CTkEntry(
            self.header, placeholder_text="🔍 Título, código ou linguagem...",
            width=380, height=40, corner_radius=12, border_width=1, font=(FONT_FAMILY, 13)
        )
        self.search_global.pack(side="left", padx=40)
        self.search_global.bind("<KeyRelease>", self._on_global_search)

        if self.on_sync_kits:
            self.sync_btn = ctk.CTkButton(
                self.header, text="🔄 Sincronizar Kits", width=160, height=40,
                fg_color="#6366F1", hover_color="#4F46E5", font=(FONT_FAMILY, 13, "bold"),
                corner_radius=12, command=self.on_sync_kits
            )
            self.sync_btn.pack(side="right")

        # --- ÁREA DE CONTEÚDO PRINCIPAL ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(expand=True, fill="both", padx=100)

        # 1. Container do Grid de Cards (Padrão)
        self.grid_wrapper = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.grid_wrapper.pack(expand=True, fill="both")

        # 2. Container de Resultados de Busca (Inicia Oculto)
        self.results_wrapper = ctk.CTkScrollableFrame(
            self.main_content, fg_color=COLOR_BG, corner_radius=15, 
            border_width=1, border_color="#E2E8F0"
        )

        self._render_cards(categories)

    def _render_cards(self, categories):
        for i in range(4):
            self.grid_wrapper.grid_columnconfigure(i, weight=1)

        items = [(c[0], c[1], c[2] if c[1] != "Utilitários" else "⚡") for c in categories]
        items.append((None, "Meus Snippets", "📂"))
        
        for i, item in enumerate(items):
            _, name, icon = item
            cmd = lambda n=name: self.on_category_select(n)
            color = self.kit_colors.get(name, "#333333")
            
            card = CategoryCard(self.grid_wrapper, name=name, icon=icon, icon_color=color, command=cmd)
            card.grid(row=i // 4, column=i % 4, padx=10, pady=5)

    def _on_global_search(self, event=None):
        query = self.search_global.get().strip().lower()
        
        if not query:
            # Se a busca estiver vazia, volta para os cards
            self.results_wrapper.pack_forget()
            self.grid_wrapper.pack(expand=True, fill="both")
            return

        # Esconde os cards e mostra a lista de busca
        self.grid_wrapper.pack_forget()
        self.results_wrapper.pack(expand=True, fill="both", pady=(0, 20))

        # Limpa resultados anteriores
        for child in self.results_wrapper.winfo_children():
            child.destroy()

        # Busca no Banco (Acessando via App -> Database)
        results = self.master.master.db.search_all_snippets(query)

        if not results:
            ctk.CTkLabel(self.results_wrapper, text="Nenhum snippet encontrado.", font=(FONT_FAMILY, 14), text_color="#64748B").pack(pady=40)
            return

        for snip in results:
            # snip: (id, cat_id, title, lang, code, version, is_custom, cat_name)
            item = ctk.CTkFrame(self.results_wrapper, fg_color=COLOR_CARD, height=55, corner_radius=10)
            item.pack(fill="x", pady=4, padx=10)
            item.pack_propagate(False)

            # TAGS (Tipo, Kit, Linguagem)
            t_text, t_bg, t_col = ("CUSTOM", "#E0F2FE", "#0369A1") if snip[6] else ("PADRÃO", "#FFEDD5", "#C2410C")
            ctk.CTkLabel(item, text=t_text, font=(FONT_FAMILY, 8, "bold"), width=55, height=22, fg_color=t_bg, text_color=t_col, corner_radius=4).pack(side="left", padx=(15, 5))
            ctk.CTkLabel(item, text=snip[7].upper(), font=(FONT_FAMILY, 8, "bold"), width=85, height=22, fg_color="#F1F5F9", text_color="#64748B", corner_radius=4).pack(side="left", padx=5)
            ctk.CTkLabel(item, text=snip[3].upper(), font=(FONT_FAMILY, 8, "bold"), width=80, height=22, fg_color="#E2E8F0", text_color="#1E293B", corner_radius=4).pack(side="left", padx=5)

            # Botão para abrir
            ctk.CTkButton(
                item, text=snip[2], anchor="w", fg_color="transparent", text_color=COLOR_TEXT_MAIN, 
                hover_color="#F1F5F9", font=(FONT_FAMILY, 13, "bold"),
                command=lambda n=snip[7]: self.on_category_select(n)
            ).pack(side="left", fill="both", expand=True, padx=15)