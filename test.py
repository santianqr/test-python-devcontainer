# Imports desordenados y con problemas
import datetime

# Variable sin usar
unused_variable: str = "esto no se usa"

# Línea muy larga que viola el límite de caracteres
very_long_line = (
    "Esta es una línea extremadamente larga que supera el límite recomendado de 119 caracteres de Black y"
    "probablemente cause errores de formateo"
)
print(very_long_line)
# Problemas de tipos


def bad_function(x, y):  # Sin type hints
    return x + y  # Espaciado incorrecto


def good_function(x: int, y: int) -> int:
    return x + y


# Variable redefinida
# x: int = 5
x: str = "ahora es string"  # Cambio de tipo

# Función con problemas de mypy


def process_data(data: list[int]) -> int:
    return data[0]  # Retorna int pero dice que retorna str


# Espaciado incorrecto

print(datetime.datetime.now())


def bad_spacing():
    print("mal espaciado")


# Import no usado

# Variable con nombre no descriptivo
a: int = 1
b: int = 2
c: int = a + b

print("Hello, World!")
