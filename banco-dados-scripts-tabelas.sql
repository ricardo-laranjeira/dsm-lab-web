-- ------------------------------------------------------------
-- Tabela: usuarios
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    idusuarios        INT NOT NULL AUTO_INCREMENT,
    nome              VARCHAR(45)  NULL,
    email             VARCHAR(100) NULL,
    senha             VARCHAR(200) NULL,
    ativo             TINYINT      NULL,
    data_cadastro     DATETIME     NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME     NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (idusuarios)
);

-- ------------------------------------------------------------
-- Tabela: clientes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    idclientes        INT NOT NULL AUTO_INCREMENT,
    nome              VARCHAR(45) NULL,
    telefone          VARCHAR(16) NULL,
    ativo             TINYINT     NULL,
    data_cadastro     DATETIME    NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    usuarios_id       INT         NULL,
    PRIMARY KEY (idclientes),
    INDEX fk_clientes_usuarios_idx (usuarios_id),
    CONSTRAINT fk_clientes_usuarios
        FOREIGN KEY (usuarios_id)
        REFERENCES usuarios (idusuarios)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: enderecos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS enderecos (
    idenderecos       INT NOT NULL AUTO_INCREMENT,
    cep               VARCHAR(10)  NULL,
    endereco          VARCHAR(100) NULL,
    numero            VARCHAR(5)   NULL,
    complemento       VARCHAR(45)  NULL,
    bairro            VARCHAR(100) NULL,
    cidade            VARCHAR(45)  NULL,
    estado            VARCHAR(45)  NULL,
    data_cadastro     DATETIME     NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME     NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    clientes_id       INT          NULL,
    PRIMARY KEY (idenderecos),
    INDEX fk_enderecos_clientes_idx (clientes_id),
    CONSTRAINT fk_enderecos_clientes
        FOREIGN KEY (clientes_id)
        REFERENCES clientes (idclientes)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: categorias
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
    idcategorias      INT NOT NULL AUTO_INCREMENT,
    descricao         VARCHAR(45) NULL,
    data_cadastro     DATETIME    NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (idcategorias)
);

-- ------------------------------------------------------------
-- Tabela: materiais
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS materiais (
    idmateriais       INT NOT NULL AUTO_INCREMENT,
    descricao         VARCHAR(150)  NULL,
    valor             DECIMAL(10,2) NULL,
    unidade_medida    VARCHAR(45)   NULL,
    data_cadastro     DATETIME      NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME      NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    categorias_id     INT           NULL,
    PRIMARY KEY (idmateriais),
    INDEX fk_materiais_categorias_idx (categorias_id),
    CONSTRAINT fk_materiais_categorias
        FOREIGN KEY (categorias_id)
        REFERENCES categorias (idcategorias)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: servicos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS servicos (
    idservicos        INT NOT NULL AUTO_INCREMENT,
    descricao         VARCHAR(150)  NULL,
    valor             DECIMAL(10,2) NULL,
    data_cadastro     DATETIME      NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME      NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    categorias_id     INT           NULL,
    PRIMARY KEY (idservicos),
    INDEX fk_servicos_categorias_idx (categorias_id),
    CONSTRAINT fk_servicos_categorias
        FOREIGN KEY (categorias_id)
        REFERENCES categorias (idcategorias)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: orcamentos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orcamentos (
    idorcamentos      INT NOT NULL AUTO_INCREMENT,
    validade          DATE       NULL,
    status            TINYINT(1) NULL,
    data_cadastro     DATETIME   NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME   NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    usuarios_id       INT        NULL,
    clientes_id       INT        NULL,
    PRIMARY KEY (idorcamentos),
    INDEX fk_orcamentos_usuarios_idx (usuarios_id),
    INDEX fk_orcamentos_clientes_idx (clientes_id),
    CONSTRAINT fk_orcamentos_usuarios
        FOREIGN KEY (usuarios_id)
        REFERENCES usuarios (idusuarios)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
    CONSTRAINT fk_orcamentos_clientes
        FOREIGN KEY (clientes_id)
        REFERENCES clientes (idclientes)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: agendamentos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agendamentos (
    idagendamentos    INT NOT NULL AUTO_INCREMENT,
    data              DATE     NULL,
    hora              TIME     NULL,
    data_cadastro     DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao  DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    orcamentos_id     INT      NULL,
    PRIMARY KEY (idagendamentos),
    INDEX fk_agendamentos_orcamentos_idx (orcamentos_id),
    CONSTRAINT fk_agendamentos_orcamentos
        FOREIGN KEY (orcamentos_id)
        REFERENCES orcamentos (idorcamentos)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: orcamentos_materiais (associativa N:N)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orcamentos_materiais (
    orcamentos_id  INT NOT NULL,
    materiais_id   INT NOT NULL,
    quantidade     INT NULL,
    PRIMARY KEY (orcamentos_id, materiais_id),
    INDEX fk_orcamentos_materiais_materiais_idx (materiais_id),
    INDEX fk_orcamentos_materiais_orcamentos_idx (orcamentos_id),
    CONSTRAINT fk_orcamentos_materiais_orcamentos
        FOREIGN KEY (orcamentos_id)
        REFERENCES orcamentos (idorcamentos)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
    CONSTRAINT fk_orcamentos_materiais_materiais
        FOREIGN KEY (materiais_id)
        REFERENCES materiais (idmateriais)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

-- ------------------------------------------------------------
-- Tabela: orcamentos_servicos (associativa N:N)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orcamentos_servicos (
    orcamentos_id  INT NOT NULL,
    servicos_id    INT NOT NULL,
    quantidade     INT NULL,
    PRIMARY KEY (orcamentos_id, servicos_id),
    INDEX fk_orcamentos_servicos_servicos_idx (servicos_id),
    INDEX fk_orcamentos_servicos_orcamentos_idx (orcamentos_id),
    CONSTRAINT fk_orcamentos_servicos_orcamentos
        FOREIGN KEY (orcamentos_id)
        REFERENCES orcamentos (idorcamentos)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
    CONSTRAINT fk_orcamentos_servicos_servicos
        FOREIGN KEY (servicos_id)
        REFERENCES servicos (idservicos)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);