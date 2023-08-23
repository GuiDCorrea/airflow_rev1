create table comercial.usuarios(
	cod_usuario INT IDENTITY(1,1) PRIMARY KEY,
	nome_usuario varchar(700),
	uf varchar(3),
	cidade varchar(200),
	logradouro varchar(1000),
	data_atualizado datetime default getdate(),
	bitlogado BIT,
	bitoff BIT,
	bitativo BIT,
	data_ultimo_login datetime default GETDATE()



)



create table comercial.produtos(
	cod_produto INT IDENTITY(1,1) PRIMARY KEY,
	nome_produto varchar(max),
	url_imagem varchar(max),
	marca varchar(200),
	categoria varchar(100),
	departamento varchar(100),
	subcategoria varchar(100),
	cor varchar(200),
	fator_caixa float,
	grupo varchar(200),
	atributos varchar(max),
	url_pagina varchar(max),
	cod_google int,
	data_atualizado datetime default GETDATE())



create table comercial.googleshopping(
	cod_google INT IDENTITY(1,1) PRIMARY KEY,
	ean varchar(30),
	nome_produto varchar(400),
	url_gogle varchar(max),
	url_anuncio varchar(max),
	preco float,
	seller varchar(100),
	preco_infos varchar(20),
	data_atualizado datetime default getdate(),
	cod_produto int




)


ALTER TABLE comercial.googleshopping
ADD CONSTRAINT FK_ProdutosGoogle
FOREIGN KEY (cod_produto) REFERENCES comercial.produtos(cod_produto);



create table comercial.pedidos(
	cod_pedido INT IDENTITY(1,1) PRIMARY KEY,
	cod_usuario INT,
	cod_produto INT,
	quantidade FLOAT,
	preco FLOAT,
	preco_total FLOAT,


)




ALTER TABLE comercial.pedidos
ADD CONSTRAINT FK_ProdutooTreinoproduto
FOREIGN KEY (cod_produto) REFERENCES comercial.produtos(cod_produto);


ALTER TABLE comercial.pedidos
ADD CONSTRAINT FK_UsuarioPedidos
FOREIGN KEY (cod_usuario) REFERENCES comercial.usuarios(cod_usuario);


create table comercial.treino_produto (
	cod_treino INT IDENTITY(1,1) PRIMARY KEY,
	cod_usuario FLOAT,
	cod_produto INT,
	cod_google INT,
	rating_ALS FLOAT,
	lift FLOAT,
	confianca FLOAT,
	suport FLOAT,
	rating FLOAT,



)


ALTER TABLE comercial.treino_produto
ADD CONSTRAINT FK_UsuarioTreinoproduto
FOREIGN KEY (cod_usuario) REFERENCES comercial.usuarios(cod_usuario);


ALTER TABLE comercial.treino_produto
ADD CONSTRAINT FK_UsuarioProdutoTreino
FOREIGN KEY (cod_produto) REFERENCES comercial.produtos(cod_produto);


ALTER TABLE comercial.treino_produto
ADD CONSTRAINT FK_UsuarioTreinoProdutos
FOREIGN KEY (cod_usuario) REFERENCES comercial.usuarios(cod_usuario);