import pydantic

class _PatientInfo(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="Nombre del paciente")
    age: int = pydantic.Field(..., description="Edad del paciente")
    motive: str = pydantic.Field(..., description="Motivo de la consulta")
    country: str = pydantic.Field(..., description="Pais del paciente")
    date: str = pydantic.Field(..., description="Fecha de la cita")