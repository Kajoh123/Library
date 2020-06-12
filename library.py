import uuid
import datetime

STATUSES = {
    'y': 'Wypozyczyl',
    'f': 'Brak wypozyczen'
}

BOOKSTATUSES = {
    'y': "Wypozyczona",
    'r': 'Zarezerwowana',
    'f': 'Dostepna'
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
        self._status = BOOKSTATUSES['f']

    def _generate_id(self):
        self._id = uuid.uuid4()

    def __str__(self):
        return f'{self.title} {self.category.name} strony: {self.pages} {self.author.first_name} {self.author.last_name} id: {self._id} status: {self._status}'

    def __repr__(self):
        return f'{self.title} {self.category.name} strony: {self.pages} {self.author.first_name} {self.author.last_name} id: {self._id} status: {self._status}'

class BookCategory:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

class Library:
    def __init__(self):
        self._books = []
        self._lenders = []

    def add_book(self, book):
        self._books.append(book)

    def add_lender(self, lender):
        self._lenders.append(lender)

    def lend_book(self, book, lender):
        book._status = BOOKSTATUSES['y']
        lender._status = STATUSES['y']
        lender._borrowed_books.append(book)
    
    def return_book(self, book, lender):
        book._status = BOOKSTATUSES['f']
        for b in lender._borrowed_books:
            if b.title == book.title:
                lender._borrowed_books.remove(b)
        if not lender._borrowed_books:
            lender._status = STATUSES['f']

    def get_book(self, passed_id):
        for b in self._books:
            if b._id == passed_id:
                return b

    def return_all_books(self):
        for book in self._books:
            print(book)

sample_author = Author("Jan", "Kowalski", "Poland", "Male", '1999-08-31')

any_lender = Lender("Jan", 'Nowak', "Poland", "male", '2006-08-02')

fantasy = BookCategory("Fantasy")

my_book = Book("My Title", fantasy, 360, sample_author)

my_library = Library()
my_library.add_book(my_book)
my_library.add_lender(any_lender)
my_library.lend_book(my_book, any_lender)
print(any_lender)
my_library.return_book(my_book, any_lender)
print(any_lender)
print(my_library.get_book(my_book._id))
print('---END---')
print()
