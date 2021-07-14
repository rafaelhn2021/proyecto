# Ejercicio 7 - Juego adivina el número

import random

aleatorio = random.randint(0,100) # Generamos un numero aleatorio

print("\t.:Juego adivina el número:.")

contador = 0
while True:
    numero = int(input("Digite un numero: "))
    contador += 1
    if numero>aleatorio:
        print("\tNo es el número, digita un número menor")
    elif numero<aleatorio:
        print("\tNo es el número, digita un número mayor")
    else:
        print(f"\tFelicidades, acabas de adivinar el número {aleatorio}")
        break

print(f"\nNúmero de intentos: {contador}")