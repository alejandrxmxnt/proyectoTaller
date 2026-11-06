from flask_appbuilder import Model
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship


# Cada clase hereda de Model (Flask AppBuilder). Cada atributo representa una columna de la tabla.
# Las relaciones se declaran en la tabla "padre" (lado 1) con relationship() y backref.


class Departamento(Model):
    __tablename__ = "departamentos"
    id_departamento = Column(Integer, primary_key=True)
    numero = Column(String(10), nullable=False)
    torre = Column(String(10), nullable=False)
    piso = Column(Integer, nullable=False)
    capacidad_residentes = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)  # True = ocupado, False = disponible

    personas = relationship("Persona", backref="departamento")
    estacionamientos = relationship("Estacionamiento", backref="departamento")
    paquetes = relationship("Paquete", backref="departamento")

    def __repr__(self):
        return f"{self.torre}-{self.numero}"


class Persona(Model):
    __tablename__ = "personas"
    id_persona = Column(Integer, primary_key=True)
    nombre_completo = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    celular = Column(String(20))
    correo = Column(String(120))
    tipo_persona = Column(String(20), nullable=False)  # propietario / arrendatario / familiar
    id_departamento = Column(Integer, ForeignKey("departamentos.id_departamento"), nullable=False)

    vehiculos = relationship("Vehiculo", backref="persona")
    paquetes = relationship("Paquete", backref="destinatario")

    def __repr__(self):
        return self.nombre_completo


class Estacionamiento(Model):
    __tablename__ = "estacionamientos"
    id_estacionamiento = Column(Integer, primary_key=True)
    numero = Column(String(10), unique=True, nullable=False)
    ubicacion = Column(String(100), nullable=False)
    id_departamento = Column(Integer, ForeignKey("departamentos.id_departamento"), nullable=True)
    estado = Column(Boolean, default=False, nullable=False)  # True = asignado, False = disponible

    vehiculos = relationship("Vehiculo", backref="estacionamiento")

    def __repr__(self):
        return self.numero


class Vehiculo(Model):
    __tablename__ = "vehiculos"
    id_vehiculo = Column(Integer, primary_key=True)
    patente = Column(String(15), unique=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    color = Column(String(30), nullable=False)
    id_persona = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    id_estacionamiento = Column(Integer, ForeignKey("estacionamientos.id_estacionamiento"), nullable=True)

    def __repr__(self):
        return self.patente


class EmpresaMensajeria(Model):
    __tablename__ = "empresas_mensajeria"
    id_empresa = Column(Integer, primary_key=True)
    nombre_empresa = Column(String(100), unique=True, nullable=False)
    datos_empresa = Column(String(255))
    telefono = Column(String(20))
    correo = Column(String(120))

    paquetes = relationship("Paquete", backref="empresa")

    def __repr__(self):
        return self.nombre_empresa


class Paquete(Model):
    __tablename__ = "paquetes"
    id_paquete = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresas_mensajeria.id_empresa"), nullable=False)
    id_departamento = Column(Integer, ForeignKey("departamentos.id_departamento"), nullable=False)
    id_destinatario = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    cantidad = Column(Integer, default=1, nullable=False)
    fecha_recepcion = Column(Date, nullable=False)
    hora_recepcion = Column(Time, nullable=False)
    fecha_entrega = Column(Date, nullable=True)
    hora_entrega = Column(Time, nullable=True)
    estado = Column(Boolean, default=False, nullable=False)  # True = entregado, False = disponible

    def __repr__(self):
        return f"Paquete {self.id_paquete}"
