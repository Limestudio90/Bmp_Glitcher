import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QFileDialog, QComboBox, QSlider)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import scipy.signal as signal
import tempfile
import wave  # Aggiunto per gestire file WAV

class BMPGlitchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMP Audio Glitch Art")
        self.setGeometry(100, 100, 1200, 800)
        
        self.original_data = None
        self.header_data = None
        self.pixel_data = None
        self.modified_data = None
        self.header_size = 54  # Default BMP header size, may need adjustment
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel for controls
        left_panel = QVBoxLayout()
        
        # Load image button
        self.load_btn = QPushButton("Load BMP Image")
        self.load_btn.clicked.connect(self.load_image)
        left_panel.addWidget(self.load_btn)
        
        # Effect selection
        left_panel.addWidget(QLabel("Select Effect:"))
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["Delay", "Reverb", "Distortion", "Echo", "Pitch Shift", "Low Pass Filter"])
        left_panel.addWidget(self.effect_combo)
        
        # Effect intensity slider
        left_panel.addWidget(QLabel("Effect Intensity:"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(100)
        self.intensity_slider.setValue(50)
        left_panel.addWidget(self.intensity_slider)
        
        # Apply effect button
        self.apply_btn = QPushButton("Apply Effect")
        self.apply_btn.clicked.connect(self.apply_effect)
        self.apply_btn.setEnabled(False)
        left_panel.addWidget(self.apply_btn)
        
        # Export audio button
        self.export_audio_btn = QPushButton("Export as Audio")
        self.export_audio_btn.clicked.connect(self.export_as_audio)
        self.export_audio_btn.setEnabled(False)
        left_panel.addWidget(self.export_audio_btn)
        
        # Import audio button
        self.import_audio_btn = QPushButton("Import Audio")
        self.import_audio_btn.clicked.connect(self.import_audio)
        self.import_audio_btn.setEnabled(False)
        left_panel.addWidget(self.import_audio_btn)
        
        # Save image button
        self.save_btn = QPushButton("Save Glitched Image")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        left_panel.addWidget(self.save_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_image)
        self.reset_btn.setEnabled(False)
        left_panel.addWidget(self.reset_btn)
        
        left_panel.addStretch()
        
        # Right panel for image display
        right_panel = QVBoxLayout()
        
        # Original image
        right_panel.addWidget(QLabel("Original Image:"))
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setMinimumSize(500, 300)
        self.original_image_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.original_image_label)
        
        # Glitched image
        right_panel.addWidget(QLabel("Glitched Image:"))
        self.glitched_image_label = QLabel()
        self.glitched_image_label.setAlignment(Qt.AlignCenter)
        self.glitched_image_label.setMinimumSize(500, 300)
        self.glitched_image_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.glitched_image_label)
        
        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(300)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        # Set main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open BMP Image", "", "BMP Files (*.bmp)")
        
        if file_path:
            try:
                # Read the BMP file
                with open(file_path, 'rb') as f:
                    bmp_data = f.read()
                
                # Store the original data
                self.original_data = bmp_data
                
                # Determine header size (this is simplified, might need adjustment)
                # For standard 24-bit BMP, header is typically 54 bytes
                self.header_data = bmp_data[:self.header_size]
                self.pixel_data = bmp_data[self.header_size:]
                
                # Display the original image
                pixmap = QPixmap(file_path)
                self.original_image_label.setPixmap(pixmap.scaled(
                    self.original_image_label.width(), 
                    self.original_image_label.height(),
                    Qt.KeepAspectRatio
                ))
                
                # Enable buttons
                self.apply_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.export_audio_btn.setEnabled(True)
                self.import_audio_btn.setEnabled(True)
                
                # Reset glitched image
                self.glitched_image_label.clear()
                self.modified_data = None
                self.save_btn.setEnabled(False)
                
            except Exception as e:
                print(f"Error loading image: {e}")
    
    def export_as_audio(self):
        if self.pixel_data is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as WAV Audio", "", "WAV Files (*.wav)")
        
        if file_path:
            try:
                # Convert pixel data to audio (8-bit unsigned PCM)
                audio_data = np.frombuffer(self.pixel_data, dtype=np.uint8)
                
                # Create WAV file
                with wave.open(file_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(1)  # 1 byte (8-bit)
                    wav_file.setframerate(44100)  # Standard sample rate
                    wav_file.writeframes(audio_data.tobytes())
                    
                print(f"Audio exported to {file_path}")
                
            except Exception as e:
                print(f"Error exporting audio: {e}")
    
    def import_audio(self):
        if self.header_data is None:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Import WAV Audio", "", "WAV Files (*.wav)")
        
        if file_path:
            try:
                # Read WAV file
                with wave.open(file_path, 'rb') as wav_file:
                    # Check format compatibility
                    if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 1:
                        print("Warning: Audio should be mono 8-bit for best results")
                    
                    # Read audio data
                    audio_data = wav_file.readframes(wav_file.getnframes())
                
                # Convert to numpy array
                imported_data = np.frombuffer(audio_data, dtype=np.uint8)
                
                # Make sure the imported data is the same length as the original pixel data
                if len(imported_data) != len(self.pixel_data):
                    if len(imported_data) > len(self.pixel_data):
                        imported_data = imported_data[:len(self.pixel_data)]
                    else:
                        imported_data = np.pad(imported_data, 
                                              (0, len(self.pixel_data) - len(imported_data)), 
                                              mode='constant')
                
                # Convert back to bytes
                processed_bytes = imported_data.tobytes()
                
                # Reconstruct the BMP file
                self.modified_data = self.header_data + processed_bytes
                
                # Create temporary file to display
                with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as temp:
                    temp.write(self.modified_data)
                    temp_file = temp.name
                
                # Display the modified image
                pixmap = QPixmap(temp_file)
                self.glitched_image_label.setPixmap(pixmap.scaled(
                    self.glitched_image_label.width(), 
                    self.glitched_image_label.height(),
                    Qt.KeepAspectRatio
                ))
                
                # Clean up the temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                
                # Enable save button
                self.save_btn.setEnabled(True)
                
            except Exception as e:
                print(f"Error importing audio: {e}")
    
    def apply_effect(self):
        if self.pixel_data is None:
            return
            
        effect = self.effect_combo.currentText()
        intensity = self.intensity_slider.value() / 50.0  # Normalize to 0-2 range
        
        # Convert binary data to numpy array for processing
        # Assuming 8-bit samples for simplicity
        audio_data = np.frombuffer(self.pixel_data, dtype=np.uint8)
        
        # Apply selected effect
        if effect == "Delay":
            processed_data = self.apply_delay(audio_data, intensity)
        elif effect == "Reverb":
            processed_data = self.apply_reverb(audio_data, intensity)
        elif effect == "Distortion":
            processed_data = self.apply_distortion(audio_data, intensity)
        elif effect == "Echo":
            processed_data = self.apply_echo(audio_data, intensity)
        elif effect == "Pitch Shift":
            processed_data = self.apply_pitch_shift(audio_data, intensity)
        elif effect == "Low Pass Filter":
            processed_data = self.apply_low_pass(audio_data, intensity)
        else:
            processed_data = audio_data
        
        # Convert back to bytes
        processed_bytes = processed_data.astype(np.uint8).tobytes()
        
        # Reconstruct the BMP file
        self.modified_data = self.header_data + processed_bytes
        
        # Create temporary file using tempfile module
        with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as temp:
            temp.write(self.modified_data)
            temp_file = temp.name
        
        # Display the glitched image
        pixmap = QPixmap(temp_file)
        self.glitched_image_label.setPixmap(pixmap.scaled(
            self.glitched_image_label.width(), 
            self.glitched_image_label.height(),
            Qt.KeepAspectRatio
        ))
        
        # Clean up the temporary file
        try:
            os.unlink(temp_file)
        except:
            pass
        
        # Enable save button
        self.save_btn.setEnabled(True)
    
    def apply_delay(self, data, intensity):
        # Simple delay effect
        delay_samples = int(1000 * intensity)
        output = np.zeros_like(data)
        output[delay_samples:] = data[:-delay_samples] if delay_samples > 0 else data
        # Mix with original
        return (data * 0.5 + output * 0.5).astype(data.dtype)
    
    def apply_reverb(self, data, intensity):
        # Simple reverb using multiple delays
        output = np.copy(data).astype(np.float32)
        for i in range(1, 5):
            delay = int(200 * i * intensity)
            if delay >= len(data):
                continue
            decay = 0.4 / i
            output[delay:] += data[:-delay] * decay if delay > 0 else data * decay
        
        # Normalize to prevent clipping
        if np.max(output) > 255:
            output = output * (255.0 / np.max(output))
            
        return output.astype(data.dtype)
    
    def apply_distortion(self, data, intensity):
        # Convert to float for processing
        float_data = data.astype(np.float32)
        
        # Apply distortion
        gain = 1.0 + 5.0 * intensity
        float_data = float_data * gain
        
        # Clip values
        float_data = np.clip(float_data, 0, 255)
        
        return float_data.astype(data.dtype)
    
    def apply_echo(self, data, intensity):
        # Echo effect
        delay_samples = int(2000 * intensity)
        decay = 0.6
        
        output = np.copy(data).astype(np.float32)
        if delay_samples < len(data):
            output[delay_samples:] += data[:-delay_samples] * decay if delay_samples > 0 else data * decay
        
        # Normalize
        if np.max(output) > 255:
            output = output * (255.0 / np.max(output))
            
        return output.astype(data.dtype)
    
    def apply_pitch_shift(self, data, intensity):
        # Crude pitch shift by resampling
        # This is simplified and not a true pitch shift
        factor = 1.0 + (intensity - 1.0) * 0.2  # Range 0.8 to 1.2
        
        # Resample
        length = len(data)
        indices = np.arange(0, length, factor)
        indices = indices[indices < length].astype(np.int32)
        
        output = data[indices]
        
        # Pad or truncate to original length
        if len(output) < length:
            output = np.pad(output, (0, length - len(output)), mode='constant')
        else:
            output = output[:length]
            
        return output
    
    def apply_low_pass(self, data, intensity):
        # Low-pass filter
        cutoff = 1.0 - (intensity * 0.8)  # Higher intensity = lower cutoff
        b, a = signal.butter(4, cutoff, 'low')
        filtered_data = signal.lfilter(b, a, data)
        return filtered_data.astype(data.dtype)
    
    def save_image(self):
        if self.modified_data is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Glitched Image", "", "BMP Files (*.bmp)")
        
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(self.modified_data)
            except Exception as e:
                print(f"Error saving image: {e}")
    
    def reset_image(self):
        if self.original_data is None:
            return
            
        # Reset to original pixel data
        self.pixel_data = self.original_data[self.header_size:]
        self.modified_data = None
        
        # Clear glitched image
        self.glitched_image_label.clear()
        self.save_btn.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BMPGlitchApp()
    window.show()
    sys.exit(app.exec_())