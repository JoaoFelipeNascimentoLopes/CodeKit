# Configurações Visuais do CodeKit (Foco: Minimalismo e Performance)

# Cores da Paleta
COLOR_BG = "#F5F5F5"        # Cinza muito claro (Fundo)
COLOR_CARD = "#FFFFFF"      # Branco Puro (Cards)
COLOR_TEXT_MAIN = "#2D2D2D" # Cinza Escuro (Títulos)
COLOR_TEXT_SUB = "#666666"  # Cinza Médio (Subtítulos/Linguagens)
COLOR_ACCENT = "#3B82F6"    # Azul Suave (Destaques e Botões)

# Geometria e Fontes
RADIUS_CARD = 25            # Bordas arredondadas de 25px
FONT_FAMILY = "Poppins"     # Fonte principal

# Estilos de Texto
FONT_TITLE = (FONT_FAMILY, 28, "bold")      # Título das Categorias
FONT_CARD_TITLE = (FONT_FAMILY, 18, "bold") # Nome do Kit no Card
FONT_CODE_TITLE = (FONT_FAMILY, 20, "bold") # Nome do Snippet na Visualização
FONT_UI_REGULAR = (FONT_FAMILY, 14)         # Textos auxiliares

# Configurações para o CustomTkinter (Dicionário de aparência)
THEME_CONFIG = {
    "appearance_mode": "light",
    "color_theme": "blue",  # Tema base para widgets nativos
    "card_style": {
        "fg_color": COLOR_CARD,
        "corner_radius": RADIUS_CARD,
        "border_width": 0
    }
}

# Caminhos de Assets (Placeholder para organização)
# Os ícones devem ser salvos em assets/icons/
ASSETS_PATH = "assets/icons/"