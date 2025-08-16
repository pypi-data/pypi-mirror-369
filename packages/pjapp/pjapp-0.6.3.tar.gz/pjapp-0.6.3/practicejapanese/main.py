import sys
from practicejapanese import __version__ as VERSION
from practicejapanese.quizzes import audio_quiz, vocab_quiz, kanji_quiz
from practicejapanese.core.quiz_runner import random_quiz
from practicejapanese.core.dev_mode import run_dev_mode

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "-v":
            print(f"PracticeJapanese version {VERSION}")
            return
        elif sys.argv[1] == "-dev":
            run_dev_mode()
            return

    print("Select quiz type:")
    print("1. Random Quiz (random category each time)")
    print("2. Vocab Quiz")
    print("3. Kanji Quiz")
    print("4. Kanji Fill-in Quiz")
    print("5. Audio Quiz")
    print("6. Reset all scores")
    try:
        choice = input("Enter number: ").strip()
        if choice == "1":
            random_quiz()
        elif choice == "2":
            vocab_quiz.run()
            print()  # Add empty line after each question
        elif choice == "3":
            kanji_quiz.run()
            print()  # Add empty line after each question
        elif choice == "4":
            from practicejapanese.quizzes import filling_quiz
            filling_quiz.run()
            print()  # Add empty line after each question
        elif choice == "5":
            audio_quiz.run()
            print()  # Add empty line after each question
        elif choice == "6":
            from practicejapanese.core.utils import reset_scores
            reset_scores()
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
    except EOFError:
        # Handle Ctrl+D (EOF) gracefully
        print("\nNo input received. Goodbye!")

if __name__ == "__main__":
    main()