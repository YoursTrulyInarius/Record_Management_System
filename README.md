# Student Record Management System

A sleek, mobile-first desktop application for managing student records. Developed using Python's Tkinter framework and SQLite for local data persistence.

## Key Features
- **Mobile-First Design**: Optimized for a 400x700 aspect ratio with a clean, premium UI.
- **Auto-Generated Student IDs**: Modern 6-character random alphanumeric IDs (e.g., `STD-XJ92LK`) that are year-independent and verified for 100% uniqueness.
- **Expanded Student Profiles**: Includes **Student ID**, **Course**, and **Section/Block** fields.
- **Data Integrity & Duplicate Prevention**:
    - **Fuzzy Name Matching**: Intelligently detects duplicates even with middle initials or different casing (e.g., "John Doe" vs "JOHN D. DOE").
    - **Unique Email Constraint**: Strictly prevents multiple records using the same email address.
- **Advanced Validation**:
    - **Age**: Numeric only, positive values.
    - **Contact**: Strictly validated for exactly **11 digits**.
    - **Email**: Format validation (must contain `@`) and protection against invalid characters (quotation marks).
- **Universal Scrolling Fix**: Robust, contextual mouse-wheel scrolling implementation across all screens (View, Add, and Edit) with high-visibility scrollbars.
- **Premium Aesthetics**: Elevated cards, simulated shadows, smooth transitions, and a curated color palette.
- **Newest-First Sorting**: New records automatically appear at the top of the list for easy access.
- **Zero Dependencies**: Runs on standard Python 3.x using only built-in libraries (`tkinter`, `sqlite3`).

## Installation & Usage
1. Ensure you have **Python 3.x** installed.
2. Clone or download this repository.
3. Run the application:
   ```bash
   python main.py
   ```
### 7. Modern Student ID Format (Phase 6)
- **Year-Free Generation**: Removed the `YYYY` year component from student IDs for a more timeless design.
- **Enhanced Uniqueness**: Implemented a 6-character random alphanumeric suffix (e.g., `STD-A1B2C3`).
- **Collision Proofing**: Added a database lookup loop to ensure every generated ID is guaranteed to be unique before assignment.
## Technical Details
- **Architecture**: Single-frame container with a mobile-style Header and Bottom Navigation.
- **Database**: SQLite (`records.db`). Schema includes unique constraints and indexes for high performance and data safety.
- **Scrolling Logic**: Uses a custom contextual binding system (Enter/Leave) to manage global mouse-wheel events safely.

