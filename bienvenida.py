import dotenv
import os


def fechas_deseadas():
    print('Seleccione las fechas de preferencia para obtener un turno')
    fechas_ant = os.getenv('FECHAS')
    if fechas_ant:
        print(f'Fechas seleccionadas anteriormente: {fechas_ant}')
        while True:
            opc = input('Desea conservarlas? (si/no): ')
            if opc == 'si':
                return fechas_ant
            if opc == 'no':
                break
            print('Intente nuevamente')

    print('Ingrese a continuacion las fechas deseadas en formato DD/MM/AAAA separando cada una con guion')
    opc = input('Ejemplo: "09/08/2024 - 13/08/2024 - 14/08/2024" : ')
    if not opc:
        return ''
    opc = ' - '.join([x.strip() for x in opc.split('-')])
    return opc


def bienvenida():
    print('Bienvenido a la busqueda automatica de turnos.')
    print('Este programa ha sido testeado para obtener un turno para licencia de conducir original en Pilar.')
    print('La municipalidad utiliza un chatbot para dicho proceso.')
    print('El bot pide los siguientes datos (ENTER sin datos para salir)')

    dni = input('DNI: ')
    if not dni:
        return False

    while True:
        nacimiento = input('Fecha de nacimiento (DDMMAAAA): ')
        if not nacimiento:
            return False
        if len(nacimiento) == 8:
            if int(nacimiento[:2]) in range(1, 32) and int(nacimiento[2:4]) in range(1, 13):
                break
        print('Intente nuevamente')

    mail = input('Correo electronico: ')
    if not mail:
        return False

    fechas = fechas_deseadas()

    open('config.env', 'w').close()
    dotenv.set_key('config.env', 'DNI', dni)
    dotenv.set_key('config.env', 'NACIMIENTO', nacimiento)
    dotenv.set_key('config.env', 'CORREO', mail)
    dotenv.set_key('config.env', 'FECHAS', fechas)
    print('Configuracion guardada. Comenzando...')
