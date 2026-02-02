"""
Script para crear usuarios administradores (directiva)
"""
from app import create_app
from models import User, db
from datetime import datetime, timedelta, timezone

# Lista de administradores a crear
ADMINISTRADORES = [
    {'nombre': 'Coco', 'email': 'coco@asociacion.com', 'password': 'C7m@9K2'},
    {'nombre': 'Lidia', 'email': 'lidia@asociacion.com', 'password': 'L3p@8N4'},
    {'nombre': 'David', 'email': 'david@asociacion.com', 'password': 'D9r@4V7'},
    {'nombre': 'Bego', 'email': 'bego@asociacion.com', 'password': 'B5q@1M6'},
]

def crear_administradores():
    """Crea los usuarios administradores si no existen"""
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        creados = 0
        existentes = 0
        
        for admin_data in ADMINISTRADORES:
            # Verificar si el usuario ya existe
            usuario_existente = User.query.filter_by(email=admin_data['email']).first()
            
            if usuario_existente:
                print(f"[!] El usuario {admin_data['nombre']} ({admin_data['email']}) ya existe.")
                existentes += 1
            else:
                # Obtener la contraseña específica para este administrador
                password_usuario = admin_data.get('password')
                if not password_usuario:
                    print(f"[ERROR] No se especificó contraseña para {admin_data['nombre']} ({admin_data['email']}). Se omite la creación.")
                    continue
                
                # Crear nuevo administrador
                admin = User(
                    nombre=admin_data['nombre'],
                    email=admin_data['email'],
                    rol='directiva',
                    fecha_alta=datetime.now(timezone.utc),
                    fecha_validez=datetime.now(timezone.utc) + timedelta(days=3650)  # 10 años de validez
                )
                admin.set_password(password_usuario)
                
                db.session.add(admin)
                print(f"[OK] Usuario {admin_data['nombre']} ({admin_data['email']}) creado exitosamente.")
                creados += 1
        
        if creados > 0:
            db.session.commit()
            print(f"\n[SUCCESS] Se crearon {creados} administrador(es) exitosamente.")
        
        if existentes > 0:
            print(f"[INFO] {existentes} usuario(s) ya existian.")
        
        if creados == 0 and existentes > 0:
            print("\n[INFO] Todos los usuarios ya existen. No se realizaron cambios.")

if __name__ == '__main__':
    crear_administradores()

