import enum


class TipoDocumento(str, enum.Enum):
    DNI = "DNI"
    Pasaporte = "Pasaporte"
    Carnet_de_Extranjeria = "Carnet de Extranjeria"


class EstadoBoarding(str, enum.Enum):
    Emitido = "Emitido"
    Check_in = "Check-in"
    Embarcado = "Embarcado"
    No_show = "No-show"
    Cancelado = "Cancelado"


class NombreCategoriaMigratoria(str, enum.Enum):
    Nacional = "Nacional"
    Internacional = "Internacional"
    Transito = "Transito"


class EstadoVuelo(str, enum.Enum):
    Programado = "Programado"
    Embarcando = "Embarcando"
    Despegado = "Despegado"
    Aterrizado = "Aterrizado"
    Retrasado = "Retrasado"
    Cancelado = "Cancelado"
