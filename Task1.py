'''Task 1 :
Implement a Library Management System
Objective:
Create a Library Management System in Python. This project will involve creating classes to represent books and library members, using functions to handle various operations, and managing exceptions to ensure the system runs smoothly. 
The system should be able to:
1.	Add new books to the library.
2.	Register new members.
3.	Allow members to borrow and return books.
4.	Keep track of borrowed books and available books.
5.	Handle exceptions such as borrowing a non-existent book or returning a book not borrowed.

Requirements:
1.	Classes and Objects: Use classes to represent Books, Members, and the Library.
2.	Functions: Use functions for operations such as adding books, registering members, borrowing, and returning books.
3.	Exception Handling: Ensure the system can handle errors gracefully.'''

import json
import datetime
from pymongo import MongoClient
from tabulate import tabulate

client = MongoClient("localhost",27017)
db = client['Library']

class Book:
    def __init__(self, title,ISBN_number, author):
        self.title = title
        self.ISBN_number = ISBN_number
        self.author = author
        self.borrow_date = None
        self.return_date = None
        self.is_borrowed = False
        
class Member:
    def __init__(self, member_name,member_id,email=None):
        self.member_name = member_name
        self.member_id = member_id
        self.email = email
        self.borrowed_books = []
    
class Library:
    def __init__(self):
        self.books = [Book('Making India Awesome', 1, 'Chetan Bhagat'),
            Book('The Intelligent Investor', 2, 'Benjamin Graham'),
            Book('The Compound Effect', 3, 'Darren Hardy'),
            Book('History of Modern India',4,'Bipin Chandra'),
            Book('Rich Dad Poor Dad',5,'Robert kiyosaki'),
            Book('A Bunch of Old Letter',6,'Jawaharlal Nehru'),
            Book('Bhagavad Gita',7,'S. Radhakrishnan'),
            Book("By God's Decree",8,'Kapil Dev'),
            Book("Chitra",9,'Rabindranath Tagore'),
            Book('Divine Life',10,'Swami Shivanand')
        ]
        self.members = [Member('Mayur', 51, 'Mayur1233@gmail.com'),
            Member('Yash', 52, 'yash723@gmail.com'),
            Member('Vinit',53,'vinit90@gmail.com'),
            Member('Prathamesh',54,'prathamesh4342@gmail.com'),
            Member('Somesh',55,'somesh421@gmail.com')
        ]
        self.save_to_json()   

    def add_book(self, title,ISBN_number,author):
        for id in self.books:
            if id.ISBN_number == ISBN_number:
                raise ValueError(f"The {id.title} is already present with ISBN_number {ISBN_number} Please enter unique ISBN_number")
        book = Book(title, ISBN_number, author)
        self.books.append(book)
        self.save_to_json()
        print(f'Book "{title}" by {author} added to the library.')

    def register_member(self, member_name,member_id,email=None):
        for id in self.members:
            if id.member_id == member_id:
                raise ValueError("Member {} with member id {} is already registered, Please enter unique id".format(id.member_name,member_id))
        member = Member(member_name,member_id,email)
        self.members.append(member)
        self.save_to_json()
        print(f'Member "{member_name}" registered successfully.')

    def borrow_book(self, member_id, ISBN_Number):
        member = self.find_member(member_id)
        book = self.find_book(ISBN_Number)
        book1 = db.all_book_data.find_one({'ISBN_number':ISBN_Number})
        
        if member is None:
            raise ValueError(f'Member with ID {member_id} not found, Please registered first')
        if book is None:
            raise ValueError(f'Book with ISBN_number {ISBN_Number} not found, Please enter valid ISBN_number')  
        if book.is_borrowed:
            raise ValueError(f'Sorry, the book {book.title} with ISBN_number "{book.ISBN_number}" is already borrowed.')
        
        book.is_borrowed = True
     
        member.borrowed_books.append(book)
        book.borrow_date = datetime.datetime.now()
        self.save_to_json()
        print(f'Member "{member.member_name}" borrowed book "{book.title}" with ISBN_number is "{book.ISBN_number}".')
                
    def return_book(self, member_id, ISBN_number):
        member = self.find_member(member_id)
        book = self.find_book(ISBN_number)
        try:
            if member and book in member.borrowed_books:
                borrow_book_duration = (datetime.datetime.now() - book.borrow_date).days
                if borrow_book_duration > 7:
                    print(f"Warnig: book {book.title} with ISBN_number {book.ISBN_number} is returned late by {borrow_book_duration - 7} days")
                book.is_borrowed = False
                book.return_date = datetime.datetime.now()
                member.borrowed_books.remove(book)
              
                self.save_to_json()
                print(f'Member "{member.member_name}" returned book "{book.title}".')
            else:
                print(f'Error: Member "{member.member_name}" did not borrow "{book.title}" with ISBN_number {book.ISBN_number}".')
        except ValueError as e:
            print(e)
            
            
    def find_book(self, ISBN_number):
        for book in self.books:
            if book.ISBN_number == ISBN_number:
                return book
        return None
    
    def display_available_books(self):
        print("Available Books:")
        table_data = []
        for book in self.books:
            if not book.is_borrowed:
                table_data.append([book.title,book.ISBN_number,book.author])
        headers = ['Title','ISBN_Number','Author']
        print(tabulate(tabular_data=table_data,headers=headers,tablefmt='fancy_grid'))
      
                
    def remove_member(self,member_name,member_id):
        member = self.find_member(member_id)
        if not member:
            raise ValueError(f"{member_name} is not registered member, Please do registration first")
        self.members.remove(member)
        db.member_data.delete_one({'member_id':member_id})
        print(member_name, "delete successfully from members list")
        self.save_to_json()
        
    def save_to_json(self):
               
        with open('Book_Data.json', 'w') as file:
            for book in self.books:
                book_data = {'title': book.title,'ISBN_number':book.ISBN_number, 'author': book.author, 'is_borrowed': book.is_borrowed,'borrow_date': book.borrow_date.strftime('%Y-%m-%d %H:%M:%S') if book.borrow_date else None, "return_date" : book.return_date.strftime('%Y-%m-%d %H:%M:%S') if book.return_date else None}
                json.dump(book_data, file)
                if not db['all_book_data'].find_one({'ISBN_number':book.ISBN_number}) or book.borrow_date is not None or book.return_date is not None:
                    result = db.all_book_data.insert_one(book_data)
                file.write('\n')
        
        
        with open('member_data.json','w') as file:
            for member in self.members:
                member_data = {'name': member.member_name,'member_id':member.member_id, 'borrowed_books': [book.title for book in member.borrowed_books]}
                json.dump(member_data,file)
                file.write('\n')
                if not db['member_data'].find_one({'member_id':member.member_id}) or len(member.borrowed_books) >0:
                    db.member_data.insert_one(member_data)
                                  
        
    def find_member(self, member_id):
        for member in self.members:
            if member.member_id == member_id:
                return member
        return None        
    
    def display_avilable_members(self):
        print("Available Members:")
        table_data = [[member.member_name, member.member_id, ", ".join(book.title for book in member.borrowed_books)]for member in self.members]
        headers = ["Name","Member_ID","Borrowed_Books"]
        print(tabulate(tabular_data=table_data,headers=headers,tablefmt='fancy_grid'))
   



def display_options():
    print("\nLibrary Management System")
    print("1. Add Book")
    print("2. Register Member")
    print("3. Borrow Book")
    print("4. Return Book")
    print("5. Delete Member")
    print("6. Display Available Books")
    print("7. Available Members with borrowed books")
    print("8. Exit")
   
def main():
    obj = Library()
    while True:
        display_options()
        choice = input("Select an option: ")
        
        if choice == '1':
            try:
                title = input("Enter title of book: ")
                ISBN_number = int(input("Enter book ISBN_number: "))
                author = input("Enter author name: ")
                obj.add_book(title,ISBN_number,author)
            except ValueError as e:
                print(e)
        
        elif choice == '2':
            try:
                name = input("Enter member Name: ")
                id = int(input('Enter member id: '))
                email = input("Enter member email (optional): ")
                obj.register_member(name,id,email)
            except ValueError as e:
                print(e)
            
        elif choice == '3':
            try:
                member_id = int(input("Enter member id: "))
                book_isbn = int(input("Enter book ISBN_number: "))
                obj.borrow_book(member_id,book_isbn)
            except ValueError as e:
                print(e)
            
        elif choice == '4':
            try:
                member_id = int(input("Enter member id: "))
                book_id = int(input("Enter ISBN_number: "))
                obj.return_book(member_id, book_id)
            except ValueError:
                print("Please enter valid input")
            
        elif choice == '5':
            try:
                member_name = input("Enter Member Name: ")
                member_id = int(input('Enter Member Id: '))
                obj.remove_member(member_name,member_id)
            except ValueError as e:
                print(e)
                
        elif choice == '6':
            obj.display_available_books()
                    
        elif choice == '7':
            obj.display_avilable_members()

        else:
            choice = '8'
            return "Exit"
                       
if __name__ == '__main__':
    print(main()) 
    