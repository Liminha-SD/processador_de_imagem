# Processador de Imagens 📸

Um aplicativo desktop moderno desenvolvido em Python para processamento de imagens em lote. Ele cria composições visuais elegantes aplicando desfoque, escurecimento de fundo e sobreposição de texto vazado com a própria imagem original.

![Interface do Aplicativo](https://img.shields.io/badge/Interface-Modern_Dark-019DEA?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-GUI-green?style=for-the-badge&logo=qt&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-brown?style=for-the-badge)

---

## ✨ Funcionalidades

*   **Processamento em Lote:** Adicione múltiplas imagens de uma vez e processe todas com um clique.
*   **Interface Drag & Drop:** Arraste arquivos diretamente para a lista do aplicativo.
*   **Efeito Visual Premium:**
    *   Redimensionamento inteligente para HD (1280x720).
    *   Fundo com desfoque gaussiano e escurecimento seletivo.
    *   Texto central "vazado" que revela a imagem original nítida.
*   **Customização de Texto:** Use o nome original do arquivo ou defina um texto personalizado para todas as imagens.
*   **Marca d'Água:** Opção para adicionar créditos ou redes sociais no canto inferior direito.
*   **Multithreading:** O processamento ocorre em segundo plano, mantendo a interface responsiva.

## 🚀 Como Usar

1.  **Adicionar Imagens:** Clique em "ADICIONAR" ou arraste seus arquivos (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`) para a área central.
2.  **Configurar Texto:**
    *   Habilite "Personalizar texto central" para definir um texto fixo.
    *   Se desativado, o programa tentará extrair os primeiros 3 dígitos do nome do arquivo original.
3.  **Marca d'Água:** Ative a opção e digite seu usuário ou marca (ex: `@seu_perfil`).
4.  **Destino:** Selecione a pasta onde as novas imagens serão salvas.
5.  **Processar:** Clique em "INICIAR PROCESSAMENTO" e acompanhe a barra de progresso.

## 🛠️ Tecnologias Utilizadas

*   **[Python 3.12+](https://www.python.org/):** Linguagem base.
*   **[PySide6 (Qt for Python)](https://doc.qt.io/qtforpython/):** Interface gráfica moderna e fluida.
*   **[Pillow (PIL)](https://python-pillow.org/):** Manipulação e processamento de imagem de alta performance.
*   **[Pathlib](https://docs.python.org/3/library/pathlib.html):** Gerenciamento inteligente de caminhos de arquivos.

## 📦 Instalação para Desenvolvedores

1.  Clone este repositório.
2.  Crie um ambiente virtual:
    ```bash
    python -m venv venv
    ```
3.  Ative o ambiente virtual:
    *   Windows: `venv\Scripts\activate`
    *   Linux/Mac: `source venv/bin/activate`
4.  Instale as dependências:
    ```bash
    pip install PySide6 pillow
    ```
5.  Execute o aplicativo:
    ```bash
    python main.py
    ```

## 🔨 Gerando o Executável (.exe)

O projeto já inclui um arquivo `.spec` para facilitar a geração do executável usando o **PyInstaller**:

```bash
pyinstaller ProcessadorDeImagens.spec
```
O arquivo final estará na pasta `dist/`.

---
Desenvolvido por [Seu Nome/GitHub]
