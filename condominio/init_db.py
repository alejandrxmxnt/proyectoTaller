#Ejemplo ingeniera

#from app import app, db
#from app.models import Categoria,Ingrediente
#with app.app_context():
#    metadata = Categoria.metadata
#    engine = db.engine
#    for table in metadata.sorted_tables:
#        print("--",table.name)
#    
#    metadata.create_all(bind=engine)
#    print("Tablas creadas exitosamente.")


from app import app, db
from app.models import (
    Departamento,
    Persona,
    Estacionamiento,
    Vehiculo,
    EmpresaMensajeria,
    Paquete
)

with app.app_context():

    metadata = Departamento.metadata
    engine = db.engine

    for table in metadata.sorted_tables:
        print("--", table.name)

    metadata.create_all(bind=engine)

    print("Tablas creadas exitosamente.")