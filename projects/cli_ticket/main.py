# cli_ticket main.py
from helper import create_ticket, save_ticket, get_ai_suggestions

def main():
    while True:
        print("\nTicket Management System")
        print("1. Create Ticket")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            title = input("Enter Title: ")
            description = input("Enter Description: \n")

            if not title.strip() or not description.strip():
                print("Title and Description cannot be empty. Please try again.")
                continue

            
            new_ticket = create_ticket(title, description)
            save_ticket(new_ticket)
            print(f"Ticket {new_ticket['id']} created successfully.\n")
            print("Fetching AI suggestions for troubleshooting...")
            ai_suggestions = get_ai_suggestions(description)
            print("\nAI Suggestions:")
            print(ai_suggestions)

        elif choice == '2':
            print("Exiting Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()