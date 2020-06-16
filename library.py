import uuid
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

STATUSES = {
    'y': 'Wypozyczyl',
    'f': 'Brak wypozyczen'
}

BOOKSTATUSES = {
    'y': "Lended",
    'r': 'Reserved',
    'f': 'Available'
}

book = {
    'name': 'somename',
    'author': 'Jan Kowalski'
}

class Person:
    def __init__(self, first_name, last_name, country, gender, birthdate):
        self.first_name = first_name
        self.last_name = last_name
        self.country = country
        self.gender = gender
        self.birthdate = datetime.datetime.strptime(birthdate, '%Y-%m-%d')

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.country} {self.gender} {self.birthdate}'

    def is_of_age(self):
        if datetime.datetime.now().year - self.birthdate.year >= 18:
            return True
        return False

class Author(Person):
    def __init__(self, first_name, last_name, country, gender, birthdate):
        super().__init__(first_name, last_name, country, gender, birthdate)
        self._generate_id()

    def _generate_id(self):
        self._id = uuid.uuid4()

    def __str__(self):
        return super().__str__() + f' id: {self._id}'

    def __repr__(self):
        return super().__str__() + f' id: {self._id}'

class Lender(Person):
    def __init__(self, first_name, last_name, country, gender, birthdate):
        super().__init__(first_name, last_name, country, gender, birthdate)
        self._generate_id()
        self._status = STATUSES['f']
        self._borrowed_books = []

    def _generate_id(self):
        self._id = uuid.uuid4()

    def __str__(self):
        return super().__str__() + f' id: {self._id} {self._status} lended books: {self._borrowed_books}'

    def __repr__(self):
        return super().__str__() + f' id: {self._id} {self._status} lended books: {self._borrowed_books}'

class Book:
    def __init__(self, title, category, pages, author):
        self.title = title
        self.category = category
        self.pages = pages
        self.author = author
        self._generate_id()
        self.status = BOOKSTATUSES['f']

    def _generate_id(self):
        self._id = uuid.uuid4()

    def __str__(self):
        return f'{self.title} {self.category.name} strony: {self.pages} {self.author.first_name} {self.author.last_name} id: {self._id} status: {self.status}'

    def __repr__(self):
        return f'{self.title} {self.category.name} strony: {self.pages} {self.author.first_name} {self.author.last_name} id: {self._id} status: {self.status}'

class BookCategory:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

class Library:
    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client['librarydb']
        self.books = self.db.books
        self.lenders = self.db.lenders
        self.authors = self.db.authors
        self._books_id = []
        self._lenders_id = []
        # self.books.delete_many({})
        # self.lenders.delete_many({})

    def add_book(self, book):
        writer = 0
        for a in self.authors.find({'_id': book.author}):
            writer = a
        if writer:
            new_book = {
                'title': book.title,
                'category': book.category,
                'pages': book.pages,
                'author': writer['first_name'] + ' ' + writer['last_name'],
                'status': book.status
            }
            self._books_id.append(self.books.insert_one(new_book))
        else:
            print("This author does not exist in database. Would you like to add him instead? Use lib add author.")
    
    def show_books(self):
        for b in self.books.find({}):
            print(b)

    def show_lenders(self):
        for l in self.lenders.find({}):
            print(l)
    
    def show_authors(self):
        for a in self.authors.find({}):
            print(a)

    def convert_id_to_book(self, tab):
        ret_str = ''
        for x in tab:
            for b in self.books.find({'_id': x}):
                ret_str += b['title'] + ' ' + b['author'] + ' id: ' + str(b['_id']) + '\t'
        print(ret_str)
        return ret_str

    def show_lends(self):
        for l in self.lenders.find({}):
            somestr = self.convert_id_to_book(l['borrowed_books'])
            print(l['first_name'], ' ', l['last_name'], ' with id: ', l['_id'], 'borrowed: ', somestr)

    def add_author(self, author):
        new_author = {
            'first_name': author.first_name,
            'last_name': author.last_name, 
            'country': author.country, 
            'gender': author.gender, 
            'birthdate': author.birthdate
        }
        self.authors.insert_one(new_author)

    def add_lender(self, lender):
        new_lender = {'first_name': lender.first_name,
        'last_name': lender.last_name, 
        'country': lender.country, 
        'gender': lender.gender, 
        'birthdate': lender.birthdate,
        'borrowed_books': lender._borrowed_books
        }
        self._lenders_id.append(self.lenders.insert_one(new_lender))

    def lend_book(self, book_id, lender_id):
        for b in self.books.find({'_id': book_id}):
            checkbook = b
        if checkbook['status'] == BOOKSTATUSES['f']:
            self.books.update_one({'_id': book_id}, {
                '$set': {'status': BOOKSTATUSES['y']}
            })
            for tmp in self.lenders.find({'_id': lender_id}):
                tmp_tab = tmp['borrowed_books']
            tmp_tab.append(book_id)
            self.lenders.update_one({'_id': lender_id}, {
                '$set': {'borrowed_books': tmp_tab}
            })
        else:
            print("This book is lended!")
    
    def return_book(self, book_id, lender_id):
        for tmp in self.lenders.find({'_id': lender_id}):
            tmp_tab = tmp['borrowed_books']
        if book_id in tmp_tab:
            self.books.update_one({'_id': book_id}, {
                '$set': {'status': BOOKSTATUSES['f']}
            })
            for b in tmp_tab:
                if b == book_id:
                    tmp_tab.remove(b)
            self.lenders.update_one({'_id': lender_id}, {
                '$set': {'borrowed_books': tmp_tab}
            })
        else:
            print("This person did not lend this book.")

    # def get_book(self, passed_id):
    #     for b in self._books:
    #         if b._id == passed_id:
    #             return b

    # def return_all_books(self):
    #     for book in self._books:
    #         print(book)

def menu():
    lib = Library()
    terminator = 0
    while terminator == 0:
        choice = str(input('What do you want to do? Type: lib help for help.> '))
        if choice == 'lib help':
            print("lib add - adding new book\nlib add author - adding new author\nlib add lender - adding new lender\nlib show - showing books in database\nlib show lenders - showing all lenders stored in database\nlib show authors - shows all authors stored in database\nlib show lends - showing lenders and it's borrowed books\nlib lend - lend a book\nlib quit - end program")
        if choice == 'lib add':
            inp = str(input("Give title-category-pages-author id "))
            t,c,p,a = inp.split('-')
            if len(a) == 12 or len(a) == 24:
                lib.add_book(Book(t, c, p, ObjectId(a)))
            else:
                print("Something wrong with id length!")
        if choice == 'lib add author':
            inp = str(input("Give firstname_lastname_country_gender_birthdate "))
            f, l, c, g, b = inp.split('_')
            lib.add_author(Author(f, l, c, g, b))
        if choice == 'lib show':
            lib.show_books()
        if choice == 'lib show lenders':
            lib.show_lenders()
        if choice == 'lib show authors':
            lib.show_authors()
        if choice == 'lib show lends':
            lib.show_lends()
        if choice == 'lib lend':
            inp = str(input("Give book id-lender id "))
            bid, lid = inp.split('-')
            if len(bid) == 12 or len(bid) == 24 and len(lid) == 12 or len(lid) == 24:
                lib.lend_book(ObjectId(bid), ObjectId(lid))
            else:
                print("Something wrong with id length!")
        if choice == 'lib return':
            inp = str(input("Give book id-lender id "))
            bid, lid = inp.split('-')
            if len(bid) == 12 or len(bid) == 24 and len(lid) == 12 or len(lid) == 24:
                lib.return_book(ObjectId(bid), ObjectId(lid))
            else:
                print("Something wrong with id length!")
        if choice == 'lib add lender':
            inp = str(input("Give firstname_lastname_country_gender_birthdate "))
            f, l, c, g, b = inp.split('_')
            lib.add_lender(Lender(f, l, c, g, b))
        if choice == 'lib quit':
            terminator = 1

menu()
# sample_author = Author("Jan", "Kowalski", "Poland", "Male", '1999-08-31')

# any_lender = Lender("Jan", 'Nowak', "Poland", "male", '2006-08-02')

# fantasy = BookCategory("Fantasy")

# my_book = Book("My Title", fantasy, 360, sample_author)
# client = MongoClient('127.0.0.1', 27017)
# db = client['librarydb']
# books = db.books
# books.delete_many({})

###########################
# book_id = books.insert_one(book).inserted_id
# print(book_id)
# print(books.find_one({'_id': book_id}))
# for book in books.find({}):
#     print(book)

# my_library = Library()
# my_library.add_book(my_book)
# my_library.add_lender(any_lender)
# my_library.lend_book(my_book, any_lender)
# print(any_lender)
# my_library.return_book(my_book, any_lender)
# print(any_lender)
# print(my_library.get_book(my_book._id))