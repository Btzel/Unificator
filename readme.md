# AI-Powered Image Editor

A modern, AI-driven image editing application built with PyQt5. This project aims to combine traditional image editing capabilities with advanced AI features for an enhanced editing experience.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt-5-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4-red.svg)
![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)

## ✨ Current Features

- **Layer Management**
  - Drag-and-drop layer reordering
  - Layer visibility toggle
  - Multiple layer support
  - Automatic layer naming
  - Layer deletion

- **Canvas System**
  - Zoomable canvas (0.1x to 5.0x)
  - Pan navigation
  - Checkered background for transparency
  - Custom viewport handling

- **File Operations**
  - Support for multiple image formats (PNG, JPEG, BMP, GIF)
  - Batch image import
  - Project export with maintained layers
  - Transparent background support

- **User Interface**
  - Modern dark theme
  - Collapsible side panels
  - Layer thumbnails
  - Smooth animations
  - Scrollable layer stack

## 🚀 Planned Features & TODOs

- [ ] **AI Integration**
  - [ ] Smart object detection and segmentation
  - [ ] AI-powered image enhancement
  - [ ] Style transfer capabilities
  - [ ] Automatic background removal
  - [ ] Smart retouching tools

- [ ] **Advanced Editing Tools**
  - [ ] Brush system with pressure sensitivity
  - [ ] Selection tools (rectangle, ellipse, lasso)
  - [ ] Filters and effects
  - [ ] Color adjustment tools
  - [ ] Transform tools (rotate, scale, skew)

- [ ] **Layer Enhancements**
  - [ ] Layer groups
  - [ ] Layer masks
  - [ ] Blend modes
  - [ ] Layer effects (shadow, glow, etc.)
  - [ ] Adjustment layers

- [ ] **User Experience**
  - [ ] Keyboard shortcuts
  - [ ] Custom tool presets
  - [ ] History/undo system
  - [ ] Tool options panel
  - [ ] Status bar with tool hints

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-image-editor.git
cd ai-image-editor
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install PyQt5 opencv-python
```

4. Run the application:
```bash
python main.py
```

## 🏗️ Project Structure

```
ai-image-editor/
├── main.py              # Application entry point
├── main_window.py       # Main application window
├── widgets/
│   ├── canvas.py        # Canvas implementation
│   ├── layer_manager.py # Layer management
│   ├── layer_widget.py  # Individual layer UI
│   └── panel_manager.py # Side panel handling
├── core/
│   └── image_handler.py # Image processing operations
└── interface.ui        # Qt Designer UI file
```

## 💡 Usage

1. **Adding Images**
   - Click the "Add Layer" button
   - Select one or multiple images
   - Images will be added as separate layers

2. **Managing Layers**
   - Drag layers to reorder them
   - Toggle visibility with the eye icon
   - Delete layers with the × button
   - Click a layer to select it

3. **Navigation**
   - Middle mouse button to pan
   - Mouse wheel to zoom
   - Drag layers to reposition

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note:** This project is currently under active development. Features and implementation details may change.
