from netmiko import ConnectHandler
#import logging   Esta linea y las dos de abajo para hacer troubleshooting.

#logging.basicConfig (filename='test.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

cisco_iosxe = {
    'device_type': 'cisco_ios', # si se quiere telnet el device_type tiene que ser: cisco_ios_telnet
    'host':   '10.31.230.250',
    'username': 'admin',
    'password': 'password',
    'port' : 22,          # optional, defaults to 22 si se quiere telnet usar pouerto 23
    'secret': 'password',     # optional, defaults to ''
}

#funcion que obtiene la lista de ip's de un fichero y lo de vuelve en una variable tipo lista.

def get_lista_ips (nombre_fichero):
    with open (nombre_fichero, mode="r") as fichero_dir_ips:
        lista_ips=fichero_dir_ips.readlines()
        return lista_ips

#función para inciializar el manejador de conxión de netmiko

def abrir_conexion():
    net_connect=ConnectHandler(**cisco_iosxe)
    print ("\nConectado a:", cisco_iosxe['host'])
    return net_connect    

#función para cerrar la conexión cuando hayamos acabado.
def cerrar_conexion(net_connect):
    net_connect.disconnect()



#función para obtener los usuarios que hay confiugrados actualmente en el equipo al que conectamos devuele una lista con la configuración de usuario uno por linea.
def get_users(net_connect):
    output = net_connect.check_enable_mode ()
    if output == False:
        enable = net_connect.enable()
 
    users=net_connect.send_command("show run | i username")
    users_in_lines=users.splitlines()
    return users_in_lines


#función para verificar si ya exiten los usuarios que quremos crear. Devuelve un diccionario como clave el usuario y valor True o False en funcion de si existe o no.
def verificar_usuarios(users_in_lines):
    existe_usuario={"existe_vodafone":False, "existe_administrator":False}  
    
    for user in users_in_lines:
        user_split=user.split()
        if user_split[1] == "administrator":
            existe_usuario['existe_administrator']=True
        if user_split[1] == "vodafone":
            existe_usuario['existe_vodafone']=True
            
    return existe_usuario
                
          
#funcion para crear los usuario

def crear_usuarios(net_connect):
        
       
    cfg_list = [
        "username vodafone privilege 15 secret password",
        "username administrator privilege 15 secret password"
        ]
    cfg_output = net_connect.send_config_set(cfg_list)
    print ("\t Creados usuarios vodafone y adminstator")

#Función para eliminar los usuairos verificadno que no es ninguno de los que no quermaos eliminar.

def eliminar_usuarios(net_connect, users_in_lines):

   
    output = net_connect.check_config_mode ()

    
    if output == False:
        enable = net_connect.config_mode()
    print ("\t Borrando usuarios:")
    for user in users_in_lines:
        user_split=user.split()
        if user_split[1] not in ('admin'):
            command='no username ' + user_split[1] + ' privilege 15 password Cisco'
            print ('\t\t',command)
            output=net_connect.send_command(command,expect_string =r'confirm')

            output+=net_connect.send_command('\n',expect_string=r'#')


          
def salvar_configuracion(net_connect):
    enabled_mode = net_connect.check_enable_mode()
    if enabled_mode == False:
        enabled_mode = net_connect.enable()
    config_mode= net_connect.check_config_mode ()
    if config_mode == True:
        config_mode = net_connect.exit_config_mode()
    output=net_connect.send_command("write mem")
    
    #print ("\t", output)
    print ("\t Configuración salvada")


if __name__ == '__main__':

    lista_ips=get_lista_ips("dir-ips.txt")
    
    for ip in lista_ips:
        cisco_iosxe['host']=ip
        
        try: 
            net_connect=abrir_conexion()
        
            users=get_users(net_connect)
            existen_usuarios=verificar_usuarios(users)

            if existen_usuarios['existe_vodafone']==False and existen_usuarios['existe_administrator']== False:
                crear_usuarios(net_connect)
            eliminar_usuarios(net_connect, users)
            salvar_configuracion(net_connect)
            cerrar_conexion(net_connect)
        except:
            print ("\n No se ha podido conectar a :", ip)

