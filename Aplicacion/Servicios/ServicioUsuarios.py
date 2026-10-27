import hashlib
from Dominio.usuario import Usuario
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioUsuarios:
    def __init__(self):
        self.dao = RepositoriosDAO()
        self.intentos_fallidos = {}  # Memoria para contar intentos
        self.usuarios = []
        self.siguiente_id = 1

    def _hashear(self, texto):
        return hashlib.sha256(texto.encode()).hexdigest()

    def autenticar(self, correo, password):
        usuario = self.dao.obtener_usuario_por_correo(correo)
        if not usuario:
            usuario = self.dao.obtener_usuario_por_nombre(correo)
        if not usuario:
            usuario = self.dao.obtener_usuario_por_nombre_usuario(correo)
        
        if not usuario:
            return None
            
        if usuario.estado == 'Bloqueado':
            print("Cuenta bloqueada. Por favor, contacte soporte.")
            return None

        pass_hash = self._hashear(password)
        
        if usuario.password_hash == pass_hash:
            self.intentos_fallidos[correo] = 0 # Resetea los intentos
            return usuario
        else:
            intentos = self.intentos_fallidos.get(correo, 0) + 1
            self.intentos_fallidos[correo] = intentos
            if intentos >= 3:
                self.dao.actualizar_estado_usuario(usuario.id, 'Bloqueado')
                print(f"La cuenta {correo} ha sido bloqueada tras 3 intentos fallidos.")
            return None

    def registrar_usuario(
        self,
        nombre,
        correo,
        nombre_usuario,
        password_hash                                                                               
    ):
        self.usuarios = self.dao.obtener_usuario_por_correo(correo)
        """for usuario in self.usuarios:
            if usuario.correo == correo:
                raise ValueError("Ya existe un usuario con ese correo.")

            if usuario.nombre_usuario == nombre_usuario:
                raise ValueError("Ese nombre de usuario ya existe.")"""

        pass_hash = self._hashear(password_hash)
        nuevo_id = self.dao.insertar_usuario(nombre, correo, nombre_usuario, pass_hash)

        if nuevo_id:
            usuario = Usuario(
                id=self.siguiente_id,
                nombre=nombre,
                correo=correo,
                nombre_usuario=nombre_usuario,
                password_hash=pass_hash
            )
            return usuario
        
        return None

    def listar_usuarios(self):
        # Función exclusiva para administradores
        return self.dao.obtener_todos_usuarios()

    def cambiar_estado_usuario(self, id_usuario, estado):
        estados_validos = ['Activo', 'Inactivo', 'Bloqueado']
        if estado not in estados_validos:
            raise ValueError("El estado proporcionado no es válido.")
        return self.dao.actualizar_estado_usuario(id_usuario, estado) is not None
