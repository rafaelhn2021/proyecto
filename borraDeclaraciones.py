#!/usr/bin/python3
 
# Import the library.
import sys
import mysql.connector
from mysql.connector import errorcode



fullCmdArguments = sys.argv

 
# Assign argument list to variable.
folio=str(sys.argv[1])
print (folio)

# Capture argument list.
try:

    connection = mysql.connector.connect(host='192.168.156.2',
                              database='declaracionesdb',
                             user='declaracionesus',
                             password='declaracionespass')

    cursor = connection.cursor(buffered=True)
    curs1 = connection.cursor()
    cursp = connection.cursor()

except mysql.connector.Error as error:
    print("No fue posible abrir la BD {}".format(error))
 
# Assign argument list to variable.
def borraObservaciones(folio, seccion):
    #getids="SELECT id FROM "+ seccion +" WHERE declaraciones_id=(SELECT id FROM declaracion_declaraciones WHERE folio= %s)"
    getids="SELECT id FROM declaracion_declaraciones WHERE folio= %s"
    print(getids+str(folio))
    cursor.execute(getids,(folio,))

    first_row = cursor.fetchone()
    if first_row is not None:
        print(first_row)
        rrr=first_row[0]
        decl_id=str(rrr)
        print("aqui mero!!!!!"+decl_id)
        queryds="SELECT observaciones_id FROM " + seccion +" WHERE declaraciones_id="+decl_id
        print(queryds)
        cursor.execute(queryds)
        cursor.fetchall()
        for row in cursor:
            if row[0] is not None:
                rrr=row[0]
                id=str(rrr)
                delquery= "DELETE FROM  declaracion_observaciones WHERE id ="+id
                print(delquery)
                cursor.execute(delquery)
            else:
                print ('era nulo')




def borraDepenInfoVar(folio, seccion, campo):
    checkquery= "SELECT "+campo+" FROM declaracion_infopersonalvar WHERE (declaraciones_id=(SELECT id FROM declaracion_declaraciones WHERE folio=%s))"
    cursor.execute(checkquery,(folio,))
    cursor.fetchall()

    for row in cursor:
        if row[0] is not None:
            rrr=row[0]
            id=str(rrr)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"+id)
            delquery= "DELETE FROM "+ seccion +" WHERE id ="+id
            print(delquery)
            cursor.execute(delquery)
        else:
            print ('era nulo')



def borraDirectoInfoVar(folio, seccion, campo):
    checkquery= "SELECT id FROM declaracion_declaraciones WHERE folio= %s"
    cursor.execute(checkquery, (folio,))
    first_row = cursor.fetchone()
    rrr=first_row[0]
    print(type(rrr))
    decl_id=str(rrr)
    if first_row is not None:
        print("el query es aqui mero el del mero mero "+checkquery+"buscando esta porqueria"+decl_id)
        queryds="SELECT id  FROM "+  seccion +" WHERE "+ campo +"="+decl_id
        print(queryds)
        cursor.execute(queryds)        
        for row in cursor:
            print(">>>>>>>>>>>"+str(row[0]))
            if row[0] is not None:
                rrr=row[0]
                id=str(rrr)
                delquery= "DELETE FROM "+ seccion +" WHERE id =" +id
                print(delquery)
                cursp.execute(delquery)
                print("<<<<<<<<<<<<<<<<<<<<")
            else:
                print ('era nulo en encargos')


def borraDomicilios(folio):
    checkquery= "SELECT id FROM declaracion_declaraciones WHERE folio= %s"
    cursor.execute(checkquery, (folio,))
    first_row = cursor.fetchone()
    if first_row is not None:
        rrr=first_row[0]
        decl_id=str(rrr)
        queryds="SELECT domicilios_id  FROM declaracion_infopersonalvar WHERE declaraciones_id="+decl_id
        print("!!!!!!"+queryds)
        cursp.execute(queryds)
        cursp.fetchall()
        for rows in cursp:
            rrow=rows[0]
            id1=str(rrow)
            print(id1)
            dquery="DELETE FROM declaracion_domicilios WHERE id="+id1
            print(dquery+"<<<<<<<<<<<<<<<<<<<<<<<<<<<") 
            if rows[0] is not None:
                curs1.execute(dquery)
            else:
                print("el domicilio es nulo")


try:
    sql_set= "SET FOREIGN_KEY_CHECKS=0"
    cursor.execute(sql_set)
    borraDomicilios(folio)
    borraDepenInfoVar(folio, "declaracion_apoyos","declaraciones_id")
    borraDepenInfoVar(folio, "declaracion_activosbienes","declaraciones_id")
    borraDepenInfoVar(folio, "declaracion_bienesinmuebles","declaraciones_id")
    borraDepenInfoVar(folio, "declaracion_bienesmuebles","declaraciones_id")
    borraDepenInfoVar(folio, "declaracion_datoscurriculares","declaraciones_id")
    borraDepenInfoVar(folio, "declaracion_beneficiosgratuitos", "declaraciones_id")
    borraDirectoInfoVar(folio, "declaracion_deudasotros", "declaraciones_id")
    borraDirectoInfoVar(folio, "declaracion_empresassociedades", "declaraciones_id")   
    borraDirectoInfoVar(folio, "declaracion_bienespersonas", "id")
    borraObservaciones(folio, "declaracion_clientesprincipales")
    borraDepenInfoVar(folio, "declaracion_clientesprincipales","declaraciones_id") 
    borraObservaciones(folio, "declaracion_fideicomisos")
    borraDepenInfoVar(folio, "declaracion_fideicomisos","declaraciones_id")    
    borraObservaciones(folio, "declaracion_ingresosdeclaracion")
    borraDepenInfoVar(folio, "declaracion_ingresosdeclaracion","id")
    borraObservaciones(folio, "declaracion_inversiones")
    borraDepenInfoVar(folio, "declaracion_inversiones","declaraciones_id")
    borraObservaciones(folio, "declaracion_prestamocomodato")
    borraDepenInfoVar(folio, "declaracion_prestamocomodato","declaraciones_id")
    borraObservaciones(folio, "declaracion_socioscomerciales")
    borraDepenInfoVar(folio, "declaracion_socioscomerciales","declaraciones_id")
    borraObservaciones(folio, "declaracion_representaciones")
    borraDepenInfoVar(folio, "declaracion_representaciones","declaraciones_id")
    borraDepenInfoVar(folio, "declaracion_nacionalidades","declaraciones_id")
    borraObservaciones(folio, "declaracion_mueblesnoregistrables")
    borraDepenInfoVar(folio, "declaracion_mueblesnoregistrables","declaraciones_id")
    borraObservaciones(folio, "declaracion_membresias")
    borraDepenInfoVar(folio, "declaracion_membresias","declaraciones_id")
    borraObservaciones(folio, "declaracion_encargos")
    borraDirectoInfoVar(folio, "declaracion_encargos", "declaraciones_id")
    borraObservaciones(folio, "declaracion_experiencialaboral")
    borraDirectoInfoVar(folio, "declaracion_experiencialaboral","declaraciones_id")
# 
    borraObservaciones(folio, "declaracion_infopersonalvar")   
    checkquery= "SELECT declaraciones_id FROM declaracion_infopersonalvar WHERE (declaraciones_id=(SELECT id FROM declaracion_declaraciones WHERE folio=%s))"
    cursor.execute(checkquery,(folio,))
    checkquery=""
    print(cursor)
    cursp = connection.cursor()
    cursprov= connection.cursor()
    print("en este momento la cuenta de renglones es"+str(cursor.rowcount))
    for row in cursor:
        idd=row[0]
        id=str(idd)
        print("INNER!!!!!!!!"+id)
        innerquery="DELETE FROM declaracion_conyugedependientes WHERE declaraciones_id ="+id
        cursp.execute(innerquery)
        delquery= "DELETE FROM declaracion_infopersonalvar WHERE declaraciones_id ="+id
        cursprov.execute(delquery)


    chkquery= "DELETE FROM declaracion_declaraciones WHERE  folio=%s"
    cursor.execute(chkquery,(folio,))        

    print('hecho ')

    connection.commit()

except mysql.connector.Error as error:
    print("Fallo en el proceso!!! {}".format(error))
finally:
    if (connection.is_connected()):
        cursor.close()
        curs1.close()
        connection.close()
        print("MySQL connection is closed")
