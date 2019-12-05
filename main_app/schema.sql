DROP TABLE IF EXISTS Staff_Phone_Number;
DROP TABLE IF EXISTS Airline_Staff;
DROP TABLE IF EXISTS Airline;
DROP TABLE IF EXISTS Flight;
DROP TABLE IF EXISTS Airport;
DROP TABLE IF EXISTS Ticket;
DROP TABLE IF EXISTS Airplane;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Booking_Agent;
DROP TABLE IF EXISTS Purchase;

CREATE TABLE Airline (
    airline_name TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE Airport (
    airport_name TEXT PRIMARY KEY NOT NULL,
    city TEXT
);
CREATE TABLE Airplane (
    airline_name TEXT NOT NULL,
    plane_id INTEGER NOT NULL,
    seat_amount INTEGER NOT NULL,
    PRIMARY KEY (airline_name, plane_id),
    FOREIGN KEY (airline_name) REFERENCES Airline (airline_name)
);

CREATE TABLE Airline_Staff (
    username TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    airline_name TEXT NOT NULL,
    FOREIGN KEY (airline_name) REFERENCES Airline (airline_name) on delete cascade
);

CREATE TABLE Staff_Phone_Number (
    username TEXT NOT NULL,
    staff_phone_number TEXT NOT NULL,
    PRIMARY KEY (username, staff_phone_number),
    FOREIGN KEY (username) REFERENCES Airline_Staff (username) on delete cascade
);

CREATE TABLE Flight (
    plane_id INTEGER NOT NULL,
    flight_number TEXT NOT NULL,
    airline_name TEXT NOT NULL,
    depart_date_time TIMESTAMP NOT NULL,
    arrive_date_time TIMESTAMP NOT NULL,
    depart_airport TEXT NOT NULL,
    arrive_airport TEXT NOT NULL,
    base_price INTEGER NOT NULL,
    flight_status TEXT CHECK ( flight_status='undepartured' or flight_status='departured' or flight_status='arrived' ),
    delay_status TEXT CHECK ( delay_status='on-time' or delay_status='delayed' or delay_status='early' ),
    PRIMARY KEY (flight_number, airline_name, depart_date_time),
    FOREIGN KEY (airline_name, plane_id) REFERENCES Airplane (airline_name, plane_id) on delete cascade,
    FOREIGN KEY (depart_airport) REFERENCES Airport (airport_name) on delete cascade,
    FOREIGN KEY (arrive_airport) REFERENCES Airport (airport_name) on delete cascade
);

CREATE TABLE Customer (
    cust_email TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    building_name TEXT,
    street TEXT,
    city TEXT,
    state TEXT,
    cust_phone_number TEXT,
    passport_number TEXT NOT NULL,
    passport_expiration TEXT NOT NULL,
    passport_country TEXT NOT NULL,
    date_of_birth TEXT NOT NULL
);

CREATE TABLE Booking_Agent (
    agent_email TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    booking_agent_id INTEGER
);

CREATE TABLE Ticket (
    ticket_id INTEGER PRIMARY KEY,
    airline_name TEXT NOT NULL,
    flight_number TEXT NOT NULL,
    depart_date_time TIMESTAMP NOT NULL,
    arrive_date_time TIMESTAMP NOT NULL,
    FOREIGN KEY (airline_name, flight_number, depart_date_time) REFERENCES Flight (airline_name, flight_number, depart_date_time) on delete cascade
);

CREATE TABLE Purchase (
    ticket_id INTEGER PRIMARY KEY NOT NULL,
    cust_email TEXT NOT NULL,
    booking_agent TEXT,
    sold_price TEXT NOT NULL,
    card_type TEXT,
    card_number INTEGER,
    name_on_card TEXT,
    expire_date TEXT,
    purchase_date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES Ticket (ticket_id) on delete cascade,
    FOREIGN KEY (cust_email) REFERENCES Customer (cust_email) on delete cascade,
    FOREIGN KEY (booking_agent) REFERENCES Booking_Agent (agent_email) on delete cascade
);

create table Comments
(
	airline_name TEXT,
	flight_number TEXT,
	depart_date_time TIMESTAMP,
	cust_email TEXT
		constraint Comments_Customer_cust_email_fk
			references Customer
				on delete cascade,
	comment TEXT,
	rating INTEGER,
	constraint Comments_pk
		primary key (airline_name, flight_number, depart_date_time, cust_email),
	constraint Comments_Flight_airline_name_flight_number_depart_date_time_fk
		foreign key (airline_name, flight_number, depart_date_time) references Flight (airline_name, flight_number, depart_date_time)
			on delete cascade
);