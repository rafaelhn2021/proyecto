'''
Ejercicio 11:
Hacer un programa que simule una agenda de contactos. Crear un diccionario
donde la clave sea el nombre del usuario y el valor sea el teléfono, el
programa tendrá el siguiente menú de opciones:

1. Nuevo contacto
2. Borrar contacto
3. Ver contactos existentes
4. Salir
'''

agenda = {}

while True:
    print("\t.:MENU:.")
    print("1. Nuevo contacto")
    print("2. Borrar contacto")
    print("3. Ver contactos existentes")
    print("4. Salir")
    opcion = int(input("Digite una opcion de menu: "))

    print()

    if opcion == 1:
        nombre = input("Nombre del contacto: ")
        telefono = input("Numero de telefono: ")

        if nombre not in agenda:
            agenda[nombre] = telefono
            print("Contacto agregado!")
        else:
            print("Ese nombre de contacto ya existe")

    elif opcion==2:
        nombre = input("Nombre del contacto: ")

        if nombre in agenda:
            del(agenda[nombre])
            print("Contacto eliminado!")
        else:
            print("Ese contacto no existe")

    elif opcion==3:
        print("Agenda de contactos:")
        for clave,valor in agenda.items():
            print(f"Nombre: {clave}, Telefono: {valor}")

    elif opcion==4:
        print("Gracias por utilizar su Agenda de contactos")
        break

    else:
        print("Se equivoco de opcion de menu")

    print()
