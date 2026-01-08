from pygments import lexers, highlight
from pygments.lexers import get_lexer_by_name

class SyntaxHighlighter:
    def __init__(self):
        # Cores estilo "One Dark" ou "Monokai"
        self.token_colors = {
            'Token.Keyword': '#C678DD',
            'Token.Name.Function': '#61AFEF',
            'Token.Literal.String': '#98C379',
            'Token.Comment': '#5C6370',
            'Token.Operator': '#56B6C2',
            'Token.Name.Class': '#E5C07B',
        }

    def apply_highlight(self, text_widget, code, lang_name):
        try:
            # Remove tags antigas sem deletar o texto
            for tag in text_widget.tag_names():
                text_widget.tag_delete(tag)

            try:
                lexer = get_lexer_by_name(lang_name)
            except:
                lexer = get_lexer_by_name('text')

            # Processa o conteúdo e aplica as tags por cima do texto existente
            content = text_widget.get("1.0", "end-1c")
            start_index = "1.0"
            
            for token, value in lexer.get_tokens(content):
                end_index = text_widget.index(f"{start_index} + {len(value)} chars")
                token_type = str(token)
                
                color = self._get_color_for_token(token_type)
                if color:
                    text_widget.tag_config(token_type, foreground=color)
                    text_widget.tag_add(token_type, start_index, end_index)
                
                start_index = end_index
        except:
            pass

    def _get_color_for_token(self, token_type):
        for key, color in self.token_colors.items():
            if key in token_type: return color
        return "#ABB2BF"