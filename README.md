# LiTTApp

A simple yet powerful application to manage and review academic literature. This app allows you to add, edit, view, search, and export literature data, making it an essential tool for researchers, students, and academics. The app also supports features like dark mode, undo/redo functionality, exporting to LaTeX formats, and more.

## Features

- **Add, View, and Edit Papers**: Easily manage your literature entries, including fields like title, authors, year, DOI, categories, tags, summary, and notes.
- **Integrated Search and Filter Bar**: Quickly find specific papers using a search bar and filters for categories and tags.
- **Advanced Search**: Perform detailed searches across multiple fields such as title, authors, year, categories, and tags.
- **Undo/Redo Functionality**: Undo and redo your actions with simple keyboard shortcuts.
- **Export Options**: Export your literature list as CSV, Word, or LaTeX documents.
- **Dark Mode**: Toggle dark mode for a more comfortable viewing experience in low-light environments.
- **Auto-Save and Auto-Load**: Automatically save your work and restore it when you reopen the application.
- **Backup and Restore**: Create backups of your data and restore them easily.
- **Reminders**: Set reminders for literature-related tasks or deadlines.

## Installation

### Prerequisites
- Python 3.10
- `pip` for installing Python packages

### Steps
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/jaicdev/LiTTApp.git
    cd LiTTApp
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    ```bash
    python3 main.py
    ```

## Usage

### Main Interface
- **Add Paper**: Enter the title, authors, year, DOI, categories, tags, summary, and notes, then click "Add Paper" to save it.
- **View/Edit/Delete Paper**: Select a paper from the list and choose an action from the right-click context menu or the buttons below the list.
- **Search and Filter**: Use the search bar at the top to filter papers by title, authors, or year. Use the category and tag dropdowns to narrow your search further.
- **Statistics**: View statistics about your literature collection, including the distribution of years, categories, and tags.

### Keyboard Shortcuts
- **Ctrl + S**: Save your work.
- **Ctrl + O**: Load a saved file.
- **Ctrl + Z**: Undo the last action.
- **Ctrl + Y**: Redo the last undone action.
- **Ctrl + F**: Open the advanced search dialog.
- **Ctrl + D**: Toggle dark mode.
- **Ctrl + Q**: Quit the application.

### Exporting Data
- **Export to CSV**: Save your literature list as a CSV file.
- **Export to Word**: Generate a Word document with all your papers, including summaries and notes.
- **Export to LaTeX**: Export your literature list to a LaTeX file for academic writing.

### Backup and Restore
- **Backup**: Create a JSON backup of your data for safekeeping.
- **Restore**: Load data from a previous backup.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your improvements.

### Steps for Contributing:
1. **Fork the Repository**.
2. **Create a Branch**:
    ```bash
    git checkout -b feature/YourFeature
    ```
3. **Make Your Changes**.
4. **Commit and Push**:
    ```bash
    git commit -m "Add some feature"
    git push origin feature/YourFeature
    ```
5. **Create a Pull Request** on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the open-source community for providing the tools and libraries that made this app possible.
