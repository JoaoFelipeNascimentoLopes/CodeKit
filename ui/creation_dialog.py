import customtkinter as ctk
from ui.styles import *
from core.highlighter import SyntaxHighlighter

class CreationDialog(ctk.CTkToplevel):
    def __init__(self, master, categories, on_save, edit_mode=False, initial_data=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Armazena os dados de edição
        self.edit_mode = edit_mode
        self.initial_data = initial_data # (id, cat_id, title, lang, code, version, is_custom, cat_name)
        self.on_save = on_save
        self.highlighter = SyntaxHighlighter()
        
        # --- Configuração de Janela ---
        self.width, self.height = 1280, 720
        self.title("CodeKit Editor - " + ("Editar Snippet" if edit_mode else "Novo Snippet"))
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        
        # Centralização
        x = (self.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.winfo_screenheight() // 2) - (self.height // 2)
        self.geometry(f"+{x}+{y}")

        # Mapeamento de Linguagens
        self.lang_map = {
            "ActionScript": "as", "Ada": "ada", "Assembly": "asm", "Bash": "bash", 
            "C": "c", "C#": "csharp", "C++": "cpp", "Clojure": "clojure", 
            "CoffeeScript": "coffeescript", "CSS": "css", "Dart": "dart", "Delphi": "delphi",
            "Elixir": "elixir", "Erlang": "erlang", "Fortran": "fortran", "Go": "go", 
            "Groovy": "groovy", "Haskell": "haskell", "HTML": "html", "Java": "java", 
            "JavaScript": "javascript", "JSON": "json", "Julia": "julia", "Kotlin": "kotlin", 
            "Lisp": "lisp", "Lua": "lua", "Markdown": "md", "Objective-C": "objective-c", 
            "Pascal": "pascal", "Perl": "perl", "PHP": "php", "Portugol Studio": "portugol", "PowerShell": "powershell", 
            "Python": "python", "R": "r", "Ruby": "ruby", "Rust": "rust", "Scala": "scala", 
            "SQL": "sql", "Swift": "swift", "TypeScript": "typescript", "VB.NET": "vb.net", 
            "XML": "xml", "YAML": "yaml"
        }
        
        self.cat_list = [cat[1] for cat in categories]
        self._setup_ui()
        
        if self.edit_mode and self.initial_data:
            self._load_edit_data()

        self.after(100, self.lift)
        self.grab_set()

    def _setup_ui(self):
        # --- BARRA SUPERIOR (HEADER) ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=30, pady=25)

        title_text = "✏️   Editar Snippet" if self.edit_mode else "🚀   Criar Novo Snippet"
        self.title_label = ctk.CTkLabel(
            self.top_bar, text=title_text, 
            font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXT_MAIN
        )
        self.title_label.pack(side="left")

        # --- LAYOUT PRINCIPAL ---
        self.content_layout = ctk.CTkFrame(self, fg_color="transparent")
        self.content_layout.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # PAINEL LATERAL (Configurações)
        self.side_panel = ctk.CTkFrame(
            self.content_layout, width=320, fg_color=COLOR_CARD, 
            corner_radius=20, border_width=1, border_color="#E2E8F0"
        )
        self.side_panel.pack(side="left", fill="y", padx=(0, 25))
        self.side_panel.pack_propagate(False)

        combo_style = {
            "width": 270, "height": 40, "corner_radius": 10,
            "font": (FONT_FAMILY, 13), 
            "dropdown_font": (FONT_FAMILY, 13),
            "dropdown_fg_color": "#FFFFFF", 
            "dropdown_hover_color": "#E5E7EB", 
            "dropdown_text_color": "#1F2937",
            "border_width": 1
        }

        self._create_label("Título do Snippet")
        self.entry_title = ctk.CTkEntry(self.side_panel, placeholder_text="Ex: Conexão com API", width=270, height=40, corner_radius=10)
        self.entry_title.pack(pady=(0, 15), padx=25)

        self._create_label("Categoria de Destino")
        self.combo_cat = ctk.CTkComboBox(self.side_panel, values=self.cat_list, **combo_style)
        self.combo_cat.pack(pady=(0, 15), padx=25)
        self.combo_cat.set("Meus Snippets")

        self._create_label("Linguagem")
        self.combo_lang = ctk.CTkComboBox(self.side_panel, values=sorted(list(self.lang_map.keys())), 
                                          command=lambda _: self._update_highlight(), **combo_style)
        self.combo_lang.pack(pady=(0, 15), padx=25)
        self.combo_lang.set("Python")

        self._create_label("Versão (Opcional)")
        self.entry_version = ctk.CTkEntry(self.side_panel, placeholder_text="Ex: 3.12 / ES6", width=270, height=40, corner_radius=10)
        self.entry_version.pack(pady=(0, 15), padx=25)

        # Botão salvar
        btn_text = "💾   Atualizar Snippet" if self.edit_mode else "💾   Salvar no CodeKit"
        self.btn_save = ctk.CTkButton(
            self.side_panel, text=btn_text, fg_color=COLOR_ACCENT, 
            hover_color="#1D4ED8", height=45, width=270, corner_radius=12, 
            font=(FONT_FAMILY, 14, "bold"), command=self._handle_save, cursor="hand2"
        )
        self.btn_save.pack(side="bottom", pady=25, padx=25)

        # PAINEL DO EDITOR (Lado Direito)
        self.editor_container = ctk.CTkFrame(
            self.content_layout, fg_color=COLOR_CARD, 
            corner_radius=25, border_width=1, border_color="#E2E8F0"
        )
        self.editor_container.pack(side="right", fill="both", expand=True)

        self.editor_header = ctk.CTkFrame(self.editor_container, fg_color="transparent")
        self.editor_header.pack(fill="x", padx=25, pady=(20, 0))
        
        ctk.CTkLabel(
            self.editor_header, text="EDITOR DE CÓDIGO", 
            font=(FONT_FAMILY, 11, "bold"), text_color="#64748B"
        ).pack(side="left")

        # --- EDITOR COM NÚMEROS DE LINHA ---
        self.editor_wrapper = ctk.CTkFrame(self.editor_container, fg_color="#0F172A", corner_radius=15)
        self.editor_wrapper.pack(fill="both", expand=True, padx=25, pady=25)

        # Calha de números
        self.line_numbers = ctk.CTkTextbox(
            self.editor_wrapper, width=50, font=("Consolas", 16), 
            fg_color="#070b14", text_color="#475569", border_width=0, corner_radius=0,
            activate_scrollbars=False
        )
        self.line_numbers.pack(side="left", fill="y", padx=(5, 0), pady=10)
        self.line_numbers.configure(state="disabled")

        # Widget de texto principal
        self.txt_code = ctk.CTkTextbox(
            self.editor_wrapper, fg_color="transparent", text_color="#E2E8F0",
            font=("Consolas", 16), undo=True, border_width=0
        )
        self.txt_code.pack(side="right", fill="both", expand=True, padx=5, pady=10)
        self.txt_code._textbox.configure(insertbackground="white")
        
        # Sincronização e Eventos
        self.txt_code._textbox.configure(yscrollcommand=self._sync_scroll)
        self.txt_code.bind("<KeyRelease>", self._on_text_change)
        self.txt_code.bind("<MouseWheel>", lambda e: self.after(1, self._update_line_numbers))

    def _create_label(self, text):
        ctk.CTkLabel(
            self.side_panel, text=text.upper(), 
            font=(FONT_FAMILY, 10, "bold"), text_color="#64748B"
        ).pack(anchor="w", padx=28, pady=(10, 2))

    def _sync_scroll(self, *args):
        """Sincroniza os números de linha com o scroll do editor."""
        self.line_numbers._textbox.yview_moveto(args[0])

    def _update_line_numbers(self):
        """Atualiza a barra lateral de números baseada na contagem de linhas."""
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        code_content = self.txt_code.get("1.0", "end-1c")
        line_count = code_content.count('\n') + 1
        
        lines_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", lines_string)
        
        self.line_numbers._textbox.tag_add("right", "1.0", "end")
        self.line_numbers._textbox.tag_config("right", justify="right")
        self.line_numbers.configure(state="disabled")

    def _on_text_change(self, event=None):
        """Evento disparado ao digitar: atualiza números e highlight."""
        self._update_line_numbers()
        self._update_highlight()

    def _load_edit_data(self):
        """Preenche a tela com os dados vindos do visualizador."""
        # 1. Título
        self.entry_title.insert(0, self.initial_data[2])
        
        # 2. Categoria (Sincronização Corrigida)
        if len(self.initial_data) > 7:
            self.combo_cat.set(self.initial_data[7])
        
        # 3. Linguagem
        for name, key in self.lang_map.items():
            if key == self.initial_data[3]:
                self.combo_lang.set(name)
                break
        
        # 4. Código e Versão
        self.txt_code.insert("1.0", self.initial_data[4])
        self.entry_version.insert(0, self.initial_data[5] if self.initial_data[5] else "")
        
        # 5. Atualizar Visual
        self._update_line_numbers()
        self._update_highlight()

    def _update_highlight(self, event=None):
        lang = self.lang_map.get(self.combo_lang.get(), "text")
        self.highlighter.apply_highlight(text_widget=self.txt_code, code=self.txt_code.get("1.0", "end-1c"), lang_name=lang)

    def _handle_save(self):
        title = self.entry_title.get()
        cat = self.combo_cat.get()
        lang_name = self.combo_lang.get()
        code = self.txt_code.get("1.0", "end-1c")
        version = self.entry_version.get()
        
        if title.strip() and code.strip():
            self.on_save(cat, title, self.lang_map.get(lang_name, "text"), code, version)
            self.destroy()