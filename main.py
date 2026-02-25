import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QFileDialog,
    QCheckBox, QLineEdit, QProgressBar, QMessageBox, QAbstractItemView,
    QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


class DropListWidget(QListWidget):
    """Lista personalizada que aceita arrastar e soltar arquivos."""
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.files_dropped.emit(files)


class ImageProcessorThread(QThread):
    progress_updated = Signal(int)
    status_changed = Signal(str)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, selected_images, output_folder, use_custom_text, custom_text, watermark_text=""):
        super().__init__()
        self.selected_images = selected_images
        self.output_folder = output_folder
        self.use_custom_text = use_custom_text
        self.custom_text = custom_text
        self.watermark_text = watermark_text

    def run(self):
        try:
            out = Path(self.output_folder)
            out.mkdir(parents=True, exist_ok=True)

            custom_text_enabled = self.use_custom_text
            text_to_use = self.custom_text

            for i, path in enumerate(self.selected_images):
                img = Image.open(path)

                if custom_text_enabled and text_to_use:
                    text_for_image = text_to_use
                    output_filename_digits = f"{i+1:03d}"
                else:
                    text_for_image = ''.join(filter(str.isdigit, Path(path).stem))[:3].zfill(3)
                    output_filename_digits = text_for_image

                result = self.process_single_image(img, text_for_image, self.watermark_text)
                result.save(out / f"{output_filename_digits}.jpg", quality=95)

                self.progress_updated.emit(i + 1)
                self.status_changed.emit(f"Processando: {i+1}/{len(self.selected_images)}")

            self.status_changed.emit("Concluído!")
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(f"Erro ao processar: {str(e)}")

    def process_single_image(self, img, text, watermark=""):
        SIZE = (1280, 720)
        BLUR_RADIUS = 16
        FONT_PATH = "C:/Windows/Fonts/impact.ttf"
        DARKEN_FACTOR = 0.3

        img = img.convert("RGB").resize(SIZE, Image.LANCZOS)
        blur = img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))

        # Máscara L (grayscale) para definir onde a imagem original será visível
        mask = Image.new("L", SIZE, 0)
        draw = ImageDraw.Draw(mask)

        # --- TEXTO CENTRAL ---
        max_font_size = int(SIZE[1] * 0.7)
        font_size = max_font_size

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()
            max_font_size = int(SIZE[1] * 0.2)
            font_size = max_font_size

        while font_size > 10:
            try:
                font = ImageFont.truetype(FONT_PATH, font_size)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_width < SIZE[0] * 0.9 and text_height < SIZE[1] * 0.9:
                break
            font_size -= 5

        draw.text(
            (SIZE[0] // 2, SIZE[1] // 2),
            text,
            fill=255, # Branco na máscara = Visível (Original)
            font=font,
            anchor="mm"
        )

        # --- MARCA D'ÁGUA (Vazada também) ---
        if watermark:
            wm_font_size = 35 # Levemente maior para compensar o estilo vazado
            try:
                # Usa a mesma fonte impact para manter o estilo vazado padrão
                wm_font = ImageFont.truetype(FONT_PATH, wm_font_size)
            except:
                try:
                    wm_font = ImageFont.truetype("arial.ttf", wm_font_size)
                except:
                    wm_font = ImageFont.load_default()
            
            wm_bbox = draw.textbbox((0, 0), watermark, font=wm_font)
            wm_width = wm_bbox[2] - wm_bbox[0]
            wm_height = wm_bbox[3] - wm_bbox[1]
            
            # Posição no canto inferior direito
            wm_pos = (SIZE[0] - wm_width - 25, SIZE[1] - wm_height - 25)
            
            # Desenha na mesma máscara do texto central
            draw.text(wm_pos, watermark, fill=255, font=wm_font)

        # Aplicar escurecimento ao blur
        enhancer = ImageEnhance.Brightness(blur)
        darkened_blur = enhancer.enhance(1 - DARKEN_FACTOR)

        # Combinação: A máscara define onde fica a imagem original (nítida) 
        # e onde fica o fundo (escurecido e desfocado)
        final = Image.composite(img, darkened_blur, mask)
        return final


class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processador de Imagens")
        self.setMinimumSize(800, 750)
        self.setStyleSheet(self.get_modern_stylesheet())

        self.selected_images = []
        self.use_custom_text = False
        self.custom_text = ""
        self.processor_thread = None

        self.create_widgets()

    def get_modern_stylesheet(self):
        return """
            QMainWindow {
                background-color: #0F0F0F;
            }
            QWidget {
                background-color: #0F0F0F;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #2A2A2A;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                background-color: #121212;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #019DEA;
                background-color: #0F0F0F;
            }
            QPushButton {
                background-color: #019DEA;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00B4FF;
            }
            QPushButton:pressed {
                background-color: #007ACC;
            }
            QPushButton#secondary {
                background-color: #202020;
                color: #FFFFFF;
                border: 1px solid #303030;
                font-size: 11px;
                padding: 5px 10px;
            }
            QPushButton#secondary:hover {
                background-color: #2A2A2A;
            }
            QPushButton#danger {
                background-color: #2A1515;
                color: #FF6666;
                border: 1px solid #4A2525;
                font-size: 11px;
                padding: 5px 10px;
            }
            QPushButton#danger:hover {
                background-color: #3A1A1A;
            }
            QListWidget {
                background-color: #080808;
                border: 1px solid #1A1A1A;
                border-radius: 4px;
                padding: 2px;
                outline: none;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #121212;
            }
            QListWidget::item:selected {
                background-color: #151515;
                color: #019DEA;
            }
            QLineEdit {
                background-color: #080808;
                border: 1px solid #1A1A1A;
                border-radius: 4px;
                padding: 6px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #019DEA;
            }
            QProgressBar {
                background-color: #080808;
                border: 1px solid #1A1A1A;
                border-radius: 6px;
                text-align: center;
                height: 18px;
                font-weight: bold;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #019DEA;
                border-radius: 6px;
            }
            QCheckBox {
                spacing: 8px;
                padding: 2px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #333333;
                border-radius: 3px;
                background-color: #080808;
            }
            QCheckBox::indicator:checked {
                background-color: #019DEA;
                border: 1px solid #019DEA;
            }
            QLabel#main_title {
                color: #019DEA;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 0px;
            }
        """

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 15, 25, 25)
        main_layout.setSpacing(10)

        # Título Principal Centralizado
        title = QLabel("PROCESSADOR DE IMAGENS")
        title.setObjectName("main_title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Grupo: Seleção de Imagens
        images_group = QGroupBox("ARQUIVOS DE ENTRADA (ARRASTE AQUI)")
        images_content_layout = QHBoxLayout()
        images_content_layout.setContentsMargins(12, 18, 12, 12)
        images_content_layout.setSpacing(10)
        
        # Lista de Imagens (Customizada para Drop)
        self.image_listbox = DropListWidget()
        self.image_listbox.files_dropped.connect(self.handle_files_dropped)
        self.image_listbox.setSelectionMode(QAbstractItemView.MultiSelection)
        self.image_listbox.setMinimumHeight(220)
        images_content_layout.addWidget(self.image_listbox, 5)

        # Coluna de Botões
        side_buttons_layout = QVBoxLayout()
        side_buttons_layout.setSpacing(6)
        
        add_button = QPushButton("ADICIONAR")
        add_button.setObjectName("secondary")
        add_button.setFixedWidth(100)
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(self.browse_images)
        
        remove_button = QPushButton("REMOVER")
        remove_button.setObjectName("secondary")
        remove_button.setFixedWidth(100)
        remove_button.setCursor(Qt.PointingHandCursor)
        remove_button.clicked.connect(self.remove_selected)

        clear_button = QPushButton("LIMPAR TUDO")
        clear_button.setObjectName("danger")
        clear_button.setFixedWidth(100)
        clear_button.setCursor(Qt.PointingHandCursor)
        clear_button.clicked.connect(self.clear_all_images)
        
        side_buttons_layout.addWidget(add_button)
        side_buttons_layout.addWidget(remove_button)
        side_buttons_layout.addWidget(clear_button)
        side_buttons_layout.addStretch()
        
        images_content_layout.addLayout(side_buttons_layout, 1)
        images_group.setLayout(images_content_layout)
        main_layout.addWidget(images_group)

        # Grupo: Configurações de Texto
        config_group = QGroupBox("CONFIGURAÇÕES DE TEXTO")
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(12, 18, 12, 12)
        config_layout.setSpacing(8)

        # Texto Central
        central_text_layout = QHBoxLayout()
        self.custom_text_checkbox = QCheckBox("Personalizar texto central")
        self.custom_text_checkbox.setCursor(Qt.PointingHandCursor)
        self.custom_text_checkbox.stateChanged.connect(self.toggle_custom_text_entry)
        central_text_layout.addWidget(self.custom_text_checkbox)
        
        self.custom_text_input = QLineEdit()
        self.custom_text_input.setPlaceholderText("Texto no centro...")
        self.custom_text_input.setFixedWidth(200)
        self.custom_text_input.hide()
        central_text_layout.addWidget(self.custom_text_input)
        central_text_layout.addStretch()
        config_layout.addLayout(central_text_layout)

        # Marca d'água
        wm_layout = QHBoxLayout()
        self.wm_checkbox = QCheckBox("Adicionar Marca d'água (Canto Dir.)")
        self.wm_checkbox.setCursor(Qt.PointingHandCursor)
        self.wm_checkbox.stateChanged.connect(self.toggle_wm_entry)
        wm_layout.addWidget(self.wm_checkbox)
        
        self.wm_input = QLineEdit()
        self.wm_input.setPlaceholderText("Ex: @usuario")
        self.wm_input.setFixedWidth(150)
        self.wm_input.hide()
        wm_layout.addWidget(self.wm_input)
        wm_layout.addStretch()
        config_layout.addLayout(wm_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Grupo: Saída
        output_group = QGroupBox("DIRETÓRIO DE SAÍDA")
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(12, 18, 12, 12)
        
        dest_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setPlaceholderText("Pasta de destino...")
        dest_layout.addWidget(self.output_folder_input)

        browse_button = QPushButton("BUSCAR")
        browse_button.setObjectName("secondary")
        browse_button.setFixedWidth(80)
        browse_button.setCursor(Qt.PointingHandCursor)
        browse_button.clicked.connect(self.select_output_folder)
        dest_layout.addWidget(browse_button)
        
        output_layout.addLayout(dest_layout)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Ação Final
        self.process_button = QPushButton("INICIAR PROCESSAMENTO")
        self.process_button.setMinimumHeight(45)
        self.process_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.process_button.setCursor(Qt.PointingHandCursor)
        self.process_button.clicked.connect(self.start_processing)
        main_layout.addWidget(self.process_button)

        # Footer
        footer_frame = QFrame()
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 5, 0, 0)

        self.status_label = QLabel("PRONTO")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #019DEA; font-weight: bold; font-size: 11px;")
        footer_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        footer_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(footer_frame)
        central_widget.setLayout(main_layout)

    def toggle_custom_text_entry(self):
        self.custom_text_input.setVisible(self.custom_text_checkbox.isChecked())

    def toggle_wm_entry(self):
        self.wm_input.setVisible(self.wm_checkbox.isChecked())

    def browse_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar Imagens", "", "Imagens (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        self.add_images_to_list(files)

    def handle_files_dropped(self, files):
        self.add_images_to_list(files)

    def add_images_to_list(self, files):
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')
        added_count = 0
        
        for file in files:
            p = Path(file)
            if p.is_file() and p.suffix.lower() in valid_extensions:
                if file not in self.selected_images:
                    self.selected_images.append(file)
                    self.image_listbox.addItem(p.name)
                    added_count += 1
        
        if added_count > 0:
            self.status_label.setText(f"{added_count} ARQUIVOS ADICIONADOS")

    def remove_selected(self):
        for item in reversed(self.image_listbox.selectedItems()):
            index = self.image_listbox.row(item)
            self.image_listbox.takeItem(index)
            self.selected_images.pop(index)

    def clear_all_images(self):
        if self.selected_images:
            confirm = QMessageBox.question(
                self, "Limpar Lista", 
                "Deseja remover todas as imagens da lista?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.image_listbox.clear()
                self.selected_images.clear()
                self.status_label.setText("LISTA VAZIA")
                self.progress_bar.setValue(0)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if folder:
            self.output_folder_input.setText(folder)

    def start_processing(self):
        output_folder = self.output_folder_input.text()
        if not self.selected_images or not output_folder:
            QMessageBox.critical(self, "Erro", "Selecione as imagens e a pasta de destino.")
            return

        if self.custom_text_checkbox.isChecked() and not self.custom_text_input.text():
            QMessageBox.critical(self, "Erro", "Informe o texto personalizado.")
            return
            
        if self.wm_checkbox.isChecked() and not self.wm_input.text():
            QMessageBox.critical(self, "Erro", "Informe o texto da marca d'água.")
            return

        self.process_button.setEnabled(False)
        self.progress_bar.setMaximum(len(self.selected_images))
        self.progress_bar.setValue(0)

        wm_text = self.wm_input.text() if self.wm_checkbox.isChecked() else ""

        self.processor_thread = ImageProcessorThread(
            self.selected_images, output_folder,
            self.custom_text_checkbox.isChecked(), self.custom_text_input.text(),
            wm_text
        )
        self.processor_thread.progress_updated.connect(self.progress_bar.setValue)
        self.processor_thread.status_changed.connect(self.status_label.setText)
        self.processor_thread.finished.connect(self.processing_finished)
        self.processor_thread.error_occurred.connect(self.processing_error)
        self.processor_thread.start()

    def processing_finished(self):
        self.process_button.setEnabled(True)
        self.status_label.setText("CONCLUÍDO COM SUCESSO")

    def processing_error(self, error_message):
        self.process_button.setEnabled(True)
        self.status_label.setText("ERRO NO PROCESSO")
        QMessageBox.critical(self, "Erro", error_message)


def main():
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
