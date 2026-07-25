from pydantic import BaseModel, Field


class Consulta(BaseModel):

    pregunta: str = Field(
        ...,
        min_length=1
    )


    thread_id: str = Field(

        default="usuario_web"

    )