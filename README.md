The Campus Resource Borrow & Return Management System is a console-based Python application designed to manage the borrowing and returning of shared campus resources such as laptops, books, or equipment.
The system replaces manual logbooks with a structured, file-based digital solution that ensures:
      1. accurate tracking of resources,
      2. controlled borrowing rules,
      3. clear separation of responsibilities,
      4. and safe handling of data and errors.
The application uses JSON files for persistence, allowing all data to remain available between program runs.

System Objectives:
The system is designed to:
    1. Allow students to:
        a. view available resources,
        b. borrow resources,
        c. return borrowed resources,
        d. view their borrowing history.
    2. Allow staff to:
        a. add new resources,
        b. update resource quantities,
        c. remove resources,
        d. view all transactions,
        e. view overdue transactions.
    3. Ensure:
        a. data consistency,
        b. clear validation of user input,
        c. prevention of invalid actions,
        d. safe file reading and writing.
        
High-Level Program Flow
   1. The program starts in main.py.
   2. A FileManager instance is created to handle JSON file operations.
   3. A SystemManager instance is created to manage business rules.
   4. Existing data is loaded from JSON files into memory.
   5. The user enters their campus email.
   6. The system determines whether the user is a student or staff based on the email domain.
   7. The user is routed to the appropriate menu:
          a. student_menu.py
          b. staff_menu.py
    8. All actions are validated, executed, and saved back to JSON files.
    9. Errors are caught and displayed as clear, user-friendly messages.

Program Structure
    1. main.py — Entry Point
        Responsibilities:
          1. Initializes the system.
          2. Loads all saved data.
          3. Determines user role (student or staff).
          4. Routes the user to the correct menu.
          5. Handles startup and routing errors.
Important Design Choice:
main.py contains no business logic. All borrowing, returning, validation, and file handling is delegated to other components.

  2. SystemManager — Core Business Logic
     The SystemManager class acts as the brain of the system.
        Responsibilities:
          1. Enforces borrowing rules.
          2. Validates user input.
          3. Prevents invalid operations.
          4. Manages students, resources, and transactions.
          5. Coordinates saving and loading via FileManager.
        Key Concepts Implemented:
          1. Role-based behaviour (student vs staff).
          2. Transaction tracking.
          3. Due date calculation.
          4. Overdue detection.
          5. Centralized error handling.
     
  3. FileManager — Data Persistence Layer
     The FileManager handles only file operations.
        Responsibilities:
          1. Create missing JSON files automatically.
          2. Load data safely from JSON.
          3. Save data back to JSON.
          4. Detect corrupted or invalid files.
          5. Prevent data loss using safe write techniques.
      Design Rationale:
          Keeps file handling separate from business logic.
          Allows the system to recover gracefully from file errors.
          Ensures JSON structure consistency.

  4. student_menu.py — Student Interface
      Features:
          1. Automatic login using campus email.
          2. First-time registration if the student does not exist.
          3. Viewing available resources.
          4. Borrowing and returning resources.
          5. Viewing borrowing history.
          6. Option to return to the menu or exit after each action.
      All student actions are executed through the SystemManager.
  
  5. staff_menu.py — Staff Interface
      Features:
          1. Add, update, and remove resources.
          2. View all resources in tabular format.
          3. View all transactions.
          4. View overdue transactions.
          5. Clear navigation flow with menu control.
      Staff operations are also validated and executed through the SystemManager.
  
  6. Data Storage
      The system uses three JSON files:
          . students.json
          . resources.json
          . transactions.json
      Each file stores a list of dictionaries.
      Files are automatically created and repaired if missing or empty.
  
  7. Exception Handling Strategy
      The system uses custom exception classes to ensure predictable and user-friendly error handling.
      . System-Level Errors
          . SystemManagerError (base class)
          . ValidationError — invalid input
          . NotFoundError — missing student/resource/transaction
          . ConflictError — rule violations (e.g. borrowing unavailable resource)
     . File-Level Errors
          . FileManagerError
          . FileCorruptionError — invalid or malformed JSON
        Why this matters:
          1. Prevents program crashes.
          2. Allows clear error messages to users.
          3. Makes debugging easier.
          4. Improves program robustness.


Key Design Principles Used
    Separation of Concerns: Each part of the program handles a specific role (menus handle input, SystemManager handles logic, and FileManager handles files), keeping responsibilities clearly separated.
    Single Responsibility Principle: Each class or function does only one job, making the code easier to understand, test, and modify.
    Defensive Programming: The system checks inputs and conditions in advance to prevent invalid actions and unexpected crashes.
    Fail-safe file operations: Files are created, validated, and written safely to prevent data corruption or loss.
    Clear validation and error messaging: Custom errors provide meaningful messages so users and developers know exactly what went wrong.
    Readableand maintainable structure: The code is well-structured, clearly named, and commented, making it easy to maintain and understand.


HOW TO RUN THE PROGRAM
  This application is a console-based Python program and requires Python 3.10 or higher.
  
  Before running the program, ensure the required dependency is installed:
  
    pip install tabulate
  
  All program files (main.py, system_manager.py, file_manager.py, student_menu.py, staff_menu.py) must be in the same directory. The system uses three JSON files for persistence:
  
    students.json
    resources.json
    transactions.json
  
  These files are automatically created if they do not exist.
  
  To start the application, run:
  
    python main.py
  
  When prompted, enter a campus email address:
      Student email: @alustudent.com
      Staff email: @alueducation.com
  
  The system automatically detects the user role based on the email domain and routes the user to the appropriate menu. All actions are performed through menu options 
  and saved back to the JSON files, allowing data to persist between runs.


Conclusion
    This project demonstrates a complete, well-structured Python application that combines:
    object-oriented design,
    file handling,
    exception management,
    and role-based logic.































