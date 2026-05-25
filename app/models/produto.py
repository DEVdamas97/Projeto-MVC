# Tabela de produtos

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    preco = Column(Float, nullable=False, default=0.0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True)
     
    imagem_path = Column(String(255), nullable=True) # altere caso nao seja necessario ter uma imagem para o produto

    # Conectar produto.py com categoria.py

    categoria_id = Column(
        Integer,
        ForeignKey('categorias.id', ondelete='SET NULL'),
        nullable=True
    )
    
    categoria = relationship('Categoria', backref='produtos')
    

    # método
    @property # Nos permite acessar a URL da imagem como um atributo do produto, sem precisar chamar uma função
    def imagem_url(self):
        if self.imagem_path:
            return f"/static/{self.imagem_path}"
        else:
            return "static/img/produto_placeholder.png" # caminho para imagem padrão caso não haja uma imagem específica para o produto