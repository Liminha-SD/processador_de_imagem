# 🖼️ Processador de Imagens

Aplicação desktop desenvolvida em **Python + PySide6** para processamento em lote de imagens.

O programa redimensiona imagens para **1280x720**, aplica desfoque e escurecimento no fundo, mantém o texto central nítido e permite adicionar marca d'água opcional.

Interface moderna, simples e focada em produtividade.

---

## ✨ Funcionalidades

- Arrastar e soltar imagens
- Processamento em lote
- Redimensionamento automático (1280x720)
- Fundo desfocado com escurecimento
- Texto central automático (baseado no nome do arquivo)
- Texto central personalizado
- Marca d’água opcional no canto inferior direito
- Barra de progresso
- Interface moderna em tema escuro

---

## 🛠️ Tecnologias Utilizadas

- Python 3
- PySide6
- Pillow

---

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. (Opcional) Crie um ambiente virtual

```bash
python -m venv venv
```

Ativar no Windows:

```bash
venv\Scripts\activate
```

Ativar no Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou manualmente:

```bash
pip install PySide6 Pillow
```

---

## ▶️ Como Executar

```bash
python main.py
```

---

## 🧠 Como Funciona o Processamento

Para cada imagem:

1. A imagem é convertida para RGB.
2. É redimensionada para 1280x720.
3. Uma versão desfocada é criada com Gaussian Blur.
4. O fundo é escurecido.
5. Uma máscara define onde a imagem original ficará visível.
6. O texto central é aplicado:
   - Automático (extraído do nome do arquivo)
   - Ou personalizado
7. A imagem final é exportada em `.jpg` com qualidade 95.

---

## 🔢 Texto Automático

Se o modo personalizado estiver desativado:

- O sistema extrai os 3 primeiros dígitos do nome do arquivo.
- Caso não existam números, ele preenche com zeros (`000`).
- O nome final do arquivo será baseado nesses dígitos.

Exemplo:

```
imagem_45.png → 045.jpg
foto.png → 000.jpg
```

---

## 🔤 Fonte Utilizada

O sistema tenta utilizar:

```
C:/Windows/Fonts/impact.ttf
```

Caso não encontre, utiliza a fonte padrão do sistema.

Em Linux/macOS pode ser necessário ajustar o caminho da fonte no código.

---

## 📂 Estrutura do Projeto

```
📁 projeto/
 ├── main.py
 ├── requirements.txt
 └── README.md
```

---

## ⚠️ Observações

- Funciona melhor em Windows devido ao caminho da fonte.
- As imagens de saída são sempre exportadas como `.jpg`.
- Arquivos com o mesmo nome na pasta de destino podem ser sobrescritos.
