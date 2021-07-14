# Ejercicio 9 – Mostrar una frase sin espacios y contar

frase = input("Digite una frase: ")
frase2 = ""

for i in frase:
    if i!=" ":
        frase2 += i

frase = frase2

print(f"\nFrase final: {frase}")
print(f"N° de caracteres: {len(frase)}")
