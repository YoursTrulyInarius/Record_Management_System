# Record Management System

A sleek, mobile-first desktop application for managing personal or organization records. Developed using Python's Tkinter framework and SQLite for local data persistence.

## Features
- **Mobile-First Design**: Optimized for a 400x700 aspect ratio with a clean, modern UI.
- **Full CRUD Operations**: Create, Read, Update, and Delete records effortlessly.
- **Search Functionality**: Real-time filtering by Name, Email, or Address.
- **Advanced Validation**:
    - **Age**: Numeric only (0-9).
    - **Contact**: Strictly limited to **11 digits**.
    - **Email**: Must contain "@" and **no quotation marks**.
- **Duplicate Prevention**: Intelligently blocks duplicate entries based on Name or Email collisions.
- **Premium Aesthetics**: Elevated cards, simulated shadows, and structured data layouts for a high-end feel.
- **Zero Dependencies**: Runs on standard Python 3.x with no external libraries required.

## Installation & Usage
1. Ensure you have **Python 3.x** installed.
2. Clone or download this repository.
3. Run the application:
   ```bash
   python main.py
   ```

## Technical Details
- **Architecture**: Single-frame container with a mobile-style Header and Bottom Navigation.
- **Database**: SQLite (`records.db` is automatically created on first run).
- **Security**: SQL parameterized queries to prevent injection and safer connection handling using context managers.

## Developed by:
**Sonjeev C. Cabardo**
