class log:
    """
    Clase para manejar logs con colores, con métodos accesibles directamente como log.info(), log.warning(), etc.
    """
    COLORS = {
        "debug": "\033[92m",     # Green
        "info": "\033[94m",      # Blue
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "library": "\033[95m" # Magenta
    }
    RESET = "\033[0m"  # Reset color

    @staticmethod
    def _print(message, level):
        """
        Método interno para imprimir mensajes con colores.
        """
        color = log.COLORS.get(level, log.RESET)
        print(f"{color}[{level.upper()}] {message}{log.RESET}")

    @staticmethod
    def debug(message):
        log._print(message, "debug")

    @staticmethod
    def info(message):
        log._print(message, "info")

    @staticmethod
    def warning(message):
        log._print(message, "warning")

    @staticmethod
    def error(message):
        log._print(message, "error")

    @staticmethod
    def library(message):
        log._print(message, "library")