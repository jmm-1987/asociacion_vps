"""
Script de migración para crear la tabla registros_financieros
"""
from app import create_app
from models import db, RegistroFinanciero
from sqlalchemy import inspect, text

def migrar():
    """Crea la tabla registros_financieros si no existe"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la tabla ya existe
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            
            if 'registros_financieros' in tablas_existentes:
                print("[INFO] La tabla 'registros_financieros' ya existe")
            else:
                print("[INFO] Creando tabla 'registros_financieros'...")
                # Crear la tabla usando SQLAlchemy
                RegistroFinanciero.__table__.create(db.engine, checkfirst=True)
                print("[OK] Tabla 'registros_financieros' creada exitosamente")
            
            print("\n[SUCCESS] Migración completada")
            
        except Exception as e:
            print(f"[ERROR] Error en la migración: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrar()
